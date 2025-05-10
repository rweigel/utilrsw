def svglinks(file, links=None, link_prefix="", link_attribs=None, file_out=None, debug=False):

  import io
  from lxml import etree

  def print_(*args):
    if debug:
      print(*args)

  def get_link(id, links, link_prefix):

    print_(f"  Found <g> element with id = '{id}'")

    if links is None:
      if id.startswith(f'{link_prefix}http'):
        id = id[len(link_prefix):]
        print_(f"    link = '{id}'")
        return id
      else:
        return None

    link = None
    if isinstance(links, dict):
      if id not in links:
        print_(f"  Warning: id starting with $ not in links dict: {id}")
        return None
      link = links[id]

    if callable(links):
      link = links(id)

    if not isinstance(link, str):
      print_(f"  Warning: link for {id} is not a string: {link}")
      return None

    if link is not None:
      print_(f"    link = '{link}'")
      return link

  with open(file, 'r', encoding='utf-8') as svg_file:
    print_("Reading:", file)
    f = io.StringIO()
    f.write(svg_file.read())

  # Parse the SVG content using lxml
  svg_content = f.getvalue().encode('utf-8')
  root = etree.fromstring(svg_content)

  # Find the <g> element with the desired gid
  for element in root.iter():
    id = element.attrib.get('id')

    if id is None:
      continue

    linkable = id.startswith('http') or id.startswith(link_prefix)
    linkable = linkable and str(element.tag).endswith('g')

    if linkable:
      id = element.attrib.get('id')

      link = get_link(id, links, link_prefix)
      if link is None:
        print_("    No link found. Skipping.")
        continue

      attrib = {'href': link}
      if link_attribs is not None:
        attrib.update(link_attribs)

      # Create the <a> element
      a_element = etree.Element('a', attrib=attrib)

      # Wrap the <g> element with the <a> element
      parent = element.getparent()

      if parent is not None:
          # Replace the <g> element with the <a> element
          parent.replace(element, a_element)

      # Append the <g> element as a child of the <a> element
      a_element.append(element)

  # Convert the modified SVG back to a string
  modified_svg = etree.tostring(root, encoding='unicode', pretty_print=True)

  if file_out is not None:
    file = file_out

  # Save the modified SVG content
  with open(file, 'w') as f:
    print_("Writing:", file)
    f.write(modified_svg)

if __name__ == "__main__":
  import matplotlib.pyplot as plt

  links = {
    "$A Line": "https://www.example.com",
    "$A Text": "https://www.example.com"
  }

  fig, ax = plt.subplots()
  line, = ax.plot([1, 2, 3], [4, 5, 2], gid='$A Line')
  ax.text(2, 4, 'My Line', gid='$A Text')

  # Save the plot as SVG
  plt.savefig('links.svg', format='svg')
  plt.close(fig)

  svglinks('svglinks.svg', links, 'svglinks.modified.svg')