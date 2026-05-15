def reorder_dict(d, key_order):
  """Reorder a dictionary according to a specified key order.
  Keys in the key_order that are not in the dictionary are ignored are appended
  to the end of the ordered dictionary in their original order.
  """

  d_ordered = {key: d[key] for key in key_order if key in d}
  d_ordered.update({key: d[key] for key in d if key not in d_ordered})

  return d_ordered
