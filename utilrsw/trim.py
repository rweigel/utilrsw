def trim(label):
  if label is None:
    return label
  if isinstance(label, str):
    return label.strip()
  for i in range(0, len(label)):
    if isinstance(label[i], str):
      label[i] = trim(label[i])
  return label
