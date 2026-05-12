import sys
import argparse
import numpy as np

def get_col(csv_path, col=4, skip=5):
  with open(csv_path, 'r') as f:
    for _ in range(skip):
      next(f)
    return np.array([float(line.split(',')[col]) for line in f])

def replace_col(orig_path, out_path, replace_cols, skip=5):
  cols = [rc[0] for rc in replace_cols]
  max_col = max(cols)
  replace_data = (rc[1] for rc in replace_cols)
  with open(orig_path, 'r') as orig, open(out_path, 'w') as out:
    for _, line in zip(range(skip), orig):
      out.write(line)
    for zipped in zip(orig, *replace_data):
      line = zipped[0]
      new_cols = zipped[1:]
      fields = line.split(',')
      if len(fields) <= max_col:
        fields = [*fields, *([''] * (max_col - len(fields) + 1))]
      for col, new_val in zip(cols, new_cols):
        fields[col] = str(float(new_val))
      out.write(','.join(fields).strip() + '\n')

def main(arg_list):
  parser = argparse.ArgumentParser(
    prog='specmanip.py',
    description='Manipulates spectrum CSVs produced by Spectrum Studio',
  )
  parser.add_argument('orig')
  parser.add_argument('background')
  parser.add_argument('output')
  args = parser.parse_args(arg_list)
  background = get_col(args.background)
  orig_sum = get_col(args.background, 2)
  new_sum = orig_sum - 3 * background
  orig_avg = get_col(args.background, 3)
  new_avg = orig_avg - background
  replace_col(
    args.orig,
    args.output,
    (
      (2, new_sum),
      (3, new_avg),
      (4, background),
    ),
  )

if __name__ == '__main__':
  main(sys.argv[1:])
