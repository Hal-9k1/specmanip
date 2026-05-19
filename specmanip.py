import sys
import argparse
import numpy as np
from build.githash import HASH

DEFAULT_BACKGROUND_COL = 4
HEADER_SKIP = 5

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

def replace_col(orig_path, out_path, replace_cols, skip):
  cols = [rc[0] for rc in replace_cols]
  max_col = max(cols)
  replace_data = (rc[1] for rc in replace_cols)
  with open(orig_path, 'r') as orig_file:
    orig = iter(orig_file.readlines())
  with open(out_path, 'w') as out:
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

def parse_def(word, default=None):
  fields = word.split(':')
  if len(fields) == 1:
    filename = fields[0]
    if default is None:
      raise RuntimeError(f'Must specify a column for {filename}')
    col = default
  else:
    filename = ':'.join(fields[:-1])
    try:
      col = int(fields[-1])
      if col < 0:
        raise ValueError
    except ValueError:
      raise RuntimeError(f'Column of {filename} must be a positive integer, not "{fields[-1]}"')
  return filename, col

def replace_background_subcmd(args):
  background_file, background_col = parse_def(args.background, DEFAULT_BACKGROUND_COL)
  background = get_col(background_file, background_col, args.header_skip)
  if background is None:
    raise RuntimeError(f'"{args.background}" does not contain a background column.')
  orig_sum = get_col(args.orig, 2, args.header_skip)
  orig_avg = get_col(args.orig, 3, args.header_skip)
  orig_bg = get_col(args.orig, 4, args.header_skip)
  if orig_avg is None:
    raise RuntimeError(f'"{orig_avg}" does not appear to be a Spectrum Studio spectrum CSV.')

  _, orig_num_avgs = read_info(args.orig)
  if orig_bg is not None:
    orig_avg += orig_bg
    orig_sum += orig_num_avgs * orig_bg

  replace_col(
    orig_file,
    args.output,
    (
      (2, orig_sum - orig_num_avgs * background),
      (3, orig_avg - background),
      (4, background),
    ),
    args.header_skip,
  )

def multiply_subcmd(args):
  orig_file, modify_col = parse_def(args.orig)
  output_file, output_col = parse_def(args.output, modify_col)
  replace_col(
    orig_file,
    output_file,
    ((output_col, get_col(orig_file, modify_col, args.header_skip) * args.factor),),
    args.header_skip,
  )

def main(arg_list):
  parser = argparse.ArgumentParser(
    prog='specmanip.py',
    description='Manipulates spectrum CSVs produced by Spectrum Studio',
  )
  parser.add_argument(
    '-v', '--version',
    action='version',
    version=HASH,
  )
  subparsers = parser.add_subparsers(required=True)
  replace_background_parser = subparsers.add_parser('replace-background')
  replace_background_parser.set_defaults(
    subcmd_func=replace_background_subcmd,
  )
  replace_background_parser.add_argument(
    'orig',
    help='Original spectrum to create a modified copy of.',
  )
  replace_background_parser.add_argument(
    'background',
    metavar='background[:col]',
    help=(
      'File to copy background from. If :COLUMN is given, background is read from the COLUMN '
      f'indexed column from the file instead of the default column {DEFAULT_BACKGROUND_COL}.'
    ),
  )
  replace_background_parser.add_argument(
    'output',
    help=(
      'File to output modified copy to. May be the same file as orig. The sum '
      'spectrum (2nd) and avg spectrum (3rd) columns will be modified. The '
      'background (4th) column will be copied from background:col, replacing the '
      'existing contents if they exist.'
    ),
  )
  replace_background_parser.add_argument(
    '--no-header',
    action='store_const',
    dest='header_skip',
    const=0,
    default=HEADER_SKIP,
    help=(
      f'Does not skip the first {HEADER_SKIP} lines, the length of the Spectrum '
      'Studio output file header.'
    ),
  )
  multiply_parser = subparsers.add_parser('multiply')
  multiply_parser.set_defaults(
    subcmd_func=multiply_subcmd,
  )
  multiply_parser.add_argument(
    'orig',
    metavar='orig:col',
    help='Original spectrum to create a modified copy of and the column to operate on.',
  )
  multiply_parser.add_argument(
    'factor',
    type=float,
    help='Factor to multiply the column by in the modified copy.',
  )
  multiply_parser.add_argument(
    'output',
    metavar='output[:col]',
    help=(
      'File to output modified copy to. May be the same file as orig. If :COLUMN is '
      'given, the COLUMN index column will be replaced instead of the same column '
      'copied from orig.'
    ),
  )
  multiply_parser.add_argument(
    '--no-header',
    action='store_const',
    dest='header_skip',
    const=0,
    default=HEADER_SKIP,
    help=(
      f'Does not skip the first {HEADER_SKIP} lines, the length of the Spectrum '
      'Studio output file header.'
    ),
  )
  args = parser.parse_args(arg_list)
  args.subcmd_func(args)

if __name__ == '__main__':
  main(sys.argv[1:])
