import sys
import argparse
import numpy as np
from build.githash import HASH

def get_col(csv_path, col, skip):
  with open(csv_path, 'r') as f:
    for _ in range(skip):
      next(f)
    try:
      return np.array([float(line.split(',')[col]) for line in f])
    except IndexError:
      return None

def read_info(csv_path):
  with open(csv_path, 'r') as f:
    next(f)
    try:
      intime = int(next(f).split(',')[1])
      avgs = int(next(f).split(',')[1])
    except IndexError as e:
      raise RuntimeError(f'"{csv_path}" does not appear to be a Spectrum Studio spectrum CSV.')
  return (intime, avgs)

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

def replace_background_subcmd(args):
  background = get_col(args.background, 4, 5)
  if background is None:
    raise RuntimeError(f'"{args.background}" does not contain a background column.')
  orig_sum = get_col(args.orig, 2, 5)
  orig_avg = get_col(args.orig, 3, 5)
  orig_bg = get_col(args.orig, 4, 5)
  if orig_avg is None:
    raise RuntimeError(f'"{orig_avg}" does not appear to be a Spectrum Studio spectrum CSV.')

  _, orig_num_avgs = read_info(args.orig)
  if orig_bg is not None:
    orig_avg += orig_bg
    orig_sum += orig_num_avgs * orig_bg

  replace_col(
    args.orig,
    args.output,
    (
      (2, orig_sum - orig_num_avgs * background),
      (3, orig_avg - background),
      (4, background),
    ),
  )

def main(arg_list):
  parser = argparse.ArgumentParser(
    prog='specmanip.py',
    description='Manipulates spectrum CSVs produced by Spectrum Studio',
  )
  parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {HASH}')
  subparsers = parser.add_subparsers(required=True)
  replace_background_parser = subparsers.add_parser('replace-background')
  replace_background_parser.set_defaults(subcmd_func=replace_background_subcmd)
  replace_background_parser.add_argument('orig')
  replace_background_parser.add_argument('background')
  replace_background_parser.add_argument('output')
  args = parser.parse_args(arg_list)
  args.subcmd_func(args)

if __name__ == '__main__':
  main(sys.argv[1:])
