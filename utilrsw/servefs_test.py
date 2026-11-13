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


if __name__ == "__main__":
  unittest.main()
