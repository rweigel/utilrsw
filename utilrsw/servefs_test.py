import pathlib
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import quote

from fastapi.testclient import TestClient

from utilrsw.servefs import servefs


class ServefsPathTests(unittest.TestCase):
  def setUp(self):
    temporary = tempfile.TemporaryDirectory()
    self.addCleanup(temporary.cleanup)
    base = pathlib.Path(temporary.name).resolve()
    self.root = base / "public"
    self.root.mkdir()
    self.outside = base / "public-other"
    self.outside.mkdir()
    (self.outside / "secret.txt").write_text("outside-root fixture")
    (self.root / "file.txt").write_text("public fixture")
    (self.root / "subdir").mkdir()
    (self.root / "file-link").symlink_to(self.root / "file.txt")
    (self.root / "loop").symlink_to("loop")
    (self.root / "broken").symlink_to("missing")
    (self.root / "outside-file").symlink_to(self.outside / "secret.txt")
    (self.root / "outside-dir").symlink_to(self.outside, target_is_directory=True)
    with patch("resource.setrlimit"):
      self.client = TestClient(servefs({"root": str(self.root)}))
    self.addCleanup(self.client.close)

  def test_escape_paths_are_forbidden(self):
    paths = [
      "/%2e%2e/public-other/secret.txt",
      "/subdir/%2e%2e/%2e%2e/public-other/secret.txt",
      "/" + quote(str(self.outside / "secret.txt"), safe=""),
      "/outside-file",
      "/outside-dir/",
      "/outside-dir/secret.txt",
    ]
    for method in ("GET", "HEAD"):
      for path in paths:
        with self.subTest(method=method, path=path):
          response = self.client.request(method, path)
          self.assertEqual(response.status_code, 403)
          self.assertNotIn("outside-root fixture", response.text)

  def test_public_paths_preserve_file_and_directory_behavior(self):
    for method in ("GET", "HEAD"):
      for path in ("/file.txt", "/file-link", "/subdir/%2e%2e/file.txt"):
        with self.subTest(method=method, path=path):
          response = self.client.request(method, path)
          self.assertEqual(response.status_code, 200)
          self.assertEqual(response.headers["content-length"], str(len("public fixture")))
          self.assertEqual(response.text, "public fixture" if method == "GET" else "")
          cached = self.client.request(
            method, path,
            headers={"If-Modified-Since": response.headers["last-modified"]}
          )
          self.assertEqual(cached.status_code, 304)
      with self.subTest(method=method):
        for path in ("/missing", "/loop", "/broken"):
          self.assertEqual(self.client.request(method, path).status_code, 404)
        self.assertEqual(self.client.request(method, "/subdir/").status_code, 200)
    redirect = self.client.get("/subdir", follow_redirects=False)
    self.assertEqual(redirect.status_code, 301)
    self.assertEqual(redirect.headers["location"], "/subdir/")
    listing = self.client.get("/")
    self.assertEqual(listing.status_code, 200)
    self.assertIn('href="file.txt"', listing.text)
    self.assertIn('href="file-link"', listing.text)
    self.assertNotIn('href="outside-file"', listing.text)
    self.assertNotIn('href="outside-dir/"', listing.text)

  def test_symlinked_root_is_supported(self):
    root_link = self.root.parent / "root-link"
    root_link.symlink_to(self.root, target_is_directory=True)
    with patch("resource.setrlimit"):
      client = TestClient(servefs({"root": str(root_link)}))
    with client:
      self.assertEqual(client.get("/file.txt").text, "public fixture")
      self.assertEqual(client.get("/outside-file").status_code, 403)

  def test_allowed_external_symlinks(self):
    allowed_link = self.root.parent / "allowed-link"
    allowed_link.symlink_to(self.outside, target_is_directory=True)
    second_root = self.root.parent / "second-root"
    second_root.mkdir()
    (second_root / "other.txt").write_text("second fixture")
    (self.root / "second-file").symlink_to(second_root / "other.txt")
    with patch("resource.setrlimit"):
      client = TestClient(servefs({
        "root": str(self.root),
        "allowed_symlink_roots": [str(allowed_link), str(second_root)]
      }))
    with client:
      for method in ("GET", "HEAD"):
        for path in ("/outside-file", "/outside-dir/secret.txt"):
          with self.subTest(method=method, path=path):
            response = client.request(method, path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
              response.headers["content-length"], str(len("outside-root fixture"))
            )
            self.assertEqual(response.text, "outside-root fixture" if method == "GET" else "")
            cached = client.request(method, path, headers={
              "If-Modified-Since": response.headers["last-modified"]
            })
            self.assertEqual(cached.status_code, 304)
        self.assertEqual(client.request(method, "/outside-dir/").status_code, 200)
        self.assertEqual(client.request(method, "/outside-dir/missing").status_code, 404)
      self.assertEqual(client.get("/second-file").text, "second fixture")
      redirect = client.get("/outside-dir", follow_redirects=False)
      self.assertEqual(redirect.status_code, 301)
      self.assertEqual(redirect.headers["location"], "/outside-dir/")
      listing = client.get("/")
      self.assertIn('href="outside-file"', listing.text)
      self.assertIn('href="outside-dir/"', listing.text)
      self.assertIn('href="secret.txt"', client.get("/outside-dir/").text)

  def test_allowlist_does_not_allow_traversal_or_unlisted_targets(self):
    unlisted = self.root.parent / "public-other-sibling"
    unlisted.mkdir()
    (unlisted / "private.txt").write_text("private fixture")
    (self.root / "unlisted-file").symlink_to(unlisted / "private.txt")
    (self.outside / "escape").symlink_to(unlisted, target_is_directory=True)
    (self.root / "chained-escape").symlink_to(self.outside / "escape" / "private.txt")
    (self.root / "allowed-chain").symlink_to("outside-file")
    with patch("resource.setrlimit"):
      client = TestClient(servefs({
        "root": str(self.root),
        "allowed_symlink_roots": [str(self.outside)]
      }))
    with client:
      paths = [
        "/%2e%2e/public-other/secret.txt",
        "/subdir/%2e%2e/%2e%2e/public-other/secret.txt",
        "/" + quote(str(self.outside / "secret.txt"), safe=""),
        "/unlisted-file",
        "/outside-dir/escape/",
        "/outside-dir/escape/private.txt",
        "/chained-escape",
      ]
      for method in ("GET", "HEAD"):
        for path in paths:
          with self.subTest(method=method, path=path):
            response = client.request(method, path)
            self.assertEqual(response.status_code, 403)
            self.assertNotIn("fixture", response.text)
        self.assertEqual(client.request(method, "/allowed-chain").status_code, 200)
        self.assertEqual(client.request(method, "/file-link").status_code, 200)
      listing = client.get("/")
      self.assertNotIn('href="unlisted-file"', listing.text)
      self.assertNotIn('href="chained-escape"', listing.text)
      self.assertIn('href="allowed-chain"', listing.text)
      self.assertNotIn('href="escape/"', client.get("/outside-dir/").text)

  def test_allowed_symlink_roots_configuration(self):
    with patch("resource.setrlimit"):
      with TestClient(servefs({
        "root": str(self.root), "allowed_symlink_roots": []
      })) as client:
        self.assertEqual(client.get("/outside-file").status_code, 403)
      with self.assertRaises(TypeError):
        servefs({"root": str(self.root), "allowed_symlink_roots": str(self.outside)})
      for invalid in (self.outside / "secret.txt", self.outside / "missing"):
        with self.subTest(directory=invalid), self.assertRaises(ValueError):
          servefs({"root": str(self.root), "allowed_symlink_roots": [str(invalid)]})


if __name__ == "__main__":
  unittest.main()
