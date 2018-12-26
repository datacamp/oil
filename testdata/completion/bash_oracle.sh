#!/bin/bash
#
# Test our _init_completion builtin against the bash_completion implementaiton.
#
# Usage:
#   testdata/completion/bash_oracle.sh <function name>

SH=${SH:-bash}

argv1() {
  python -c 'import sys; print(repr(sys.argv[1]))' "$@"
}

tab-complete() {
  local code=$1

  echo
  echo 'case = {}'
  echo 'CASES.append(case)'
  echo -n 'case["code"] = '; argv1 "$code"

  local pat='^case'
  { cat testdata/completion/bash_oracle_plugins.sh; echo "$code"; } |
    $SH --rcfile /dev/null -i 2>&1 |
    egrep "$pat" || echo "ERROR: output didn't match $pat"
}

# _init_completion flags used:
# -s
# -n :
#
# Do NOT need to implement:
#
# -o '@(diff|patch)' is used once.  But it's for redirect args, which we parse
# in OSH itself.
#
# NOTE: I see _init_completion -s -n : , but I believe that's identical to
# _init_completion -s.
# Also I see '-n =+!' once, but that may be a mistake.  The most common cases
# are : and =.

codegen-header() {
  # Make everything here into a Python comment.
  awk '{ print "# " $0 }' << EOF

DO NOT EDIT -- Generated by $0

bash --version:
$(bash --version)

bash_completion:'

$(md5sum testdata/completion/bash_completion)
$(ls -l testdata/completion/bash_completion)

EOF
}

init-cases() {
  codegen-header
  echo 'CASES = []'

  tab-complete $'echo foo:bar --color=auto\t'
  # Hm := are stuck together!  That is weird.
  tab-complete $'echo foo=one:two:=three --color=auto\t'

  # readline includes quotes, and _init_completion doesn't do anything about this.
  # I think that is a mistake and I will get rid of it?
  #
  # ls "--ver<TAB> or '--ver<TAB>' does NOT complete.
  # But echo 'fro<TAB> DOES!  So that is a mistake.

  tab-complete $'echo "foo:bar|" --color=auto\t'

  # scrape tab completion
  echo
  tab-complete $'noflags foo:bar --color=auto\t'
  tab-complete $'noflags "foo:bar|" --color=auto\t'
  tab-complete $'noflags "foo:bar|\t'

  echo
  tab-complete $'s foo:bar --color=auto\t'
  tab-complete $'s foo:bar --color auto\t'

  echo
  tab-complete $'n foo:bar --color=auto\t'

  echo
  tab-complete $'n2 foo:bar --color=auto\t'
}

# Write a file that's committed
write-init-cases() {
  local out=testdata/completion/bash_oracle.py
  init-cases > $out
  wc -l $out
  echo "Wrote $out"
}

other-cases() {
  codegen-header
  echo 'CASES = []'

  tab-complete $'reassemble foo:bar --color=auto\t'
  tab-complete $'words foo:bar --color=auto\t'
}

# NOTE: This was for __reassemble_comp_words_by_ref and _get_comp_words_by_ref,
# but they turned out to trivial to implement with 'compadjust'.  I'm keeping
# this for now in case we need another example of a bash oracle.

write-other-cases() {
  local out=testdata/completion/bash_oracle_other.py
  other-cases > $out
  wc -l $out
  echo "Wrote $out"
}

# TODO: osh -i isn't easily scraped, for some reason.  Does it have something
# to do with terminal modes?
compare() {
  SH=bash tab-complete $'echo f\t'
  SH=bin/osh tab-complete $'echo f\t'
}

"$@"