# ai-phrase-checker

A small Python script that fails a draft when it uses the words, phrases and patterns AI writing overuses: "delve", "game-changer", "In today's fast-paced world", "It's not just X, it's Y", em dashes, emoji stacks, hashtag walls.

Run it on a post, comment, caption, email or DM before you send it. If it prints FAIL, rewrite the flagged lines and run it again.

One file, no packages to install, works with Python 3.8+.

## Example

```text
$ python3 check.py examples/before.txt
FAIL: 12 issue(s) in 67 words
  2 emoji (limit 1)
  5 hashtags
  line 1: openers_closers: 'in today's fast-paced world'
  line 1: words: 'leverage'
  line 3: punctuation: em dash
  line 3: structure: "it's not just X, it's Y"
  line 3: words: 'deep dive'
  line 3: words: 'nothing short of'
  line 3: words: 'remarkable'
  line 5: structure: one-line reveal question ("The result?")
  line 7: openers_closers: 'let that sink in'
  line 9: openers_closers: 'what are your thoughts'

$ python3 check.py examples/after.txt
PASS: 46 words, nothing flagged
```

## What it checks

| Check | Example |
|---|---|
| Overused words | delve, leverage, seamless, robust, landscape, tapestry, moreover |
| Openers and closers | "In today's fast-paced world", "Let that sink in", "What are your thoughts?" |
| Outreach lines | "I hope this message finds you well", "caught my eye", "circle back" |
| Comment cliches | "Great post", "Thanks for sharing", "Couldn't agree more" |
| Sentence patterns | "It's not just X, it's Y", "Not only X but also Y", "The result?" |
| Punctuation | em dash, en dash, " - " used as a pause, the single-character ellipsis |
| Emoji and hashtags | starts with an emoji, more than 1 emoji, 5 or more hashtags |
| Repetition | any word of 5+ letters used 3 or more times |

Matching ignores case and only hits whole words, so "realm" is flagged but "realmente" is not.

## Usage

```bash
python3 check.py draft.txt                       # check a file
pbpaste | python3 check.py                       # check the clipboard (macOS)
python3 check.py draft.txt --skip comment_cliches  # turn a list off
python3 check.py draft.txt --allow landscape     # let one phrase through
python3 check.py draft.txt --list my-words.txt   # add your own phrases, one per line
python3 check.py draft.txt --repeat 0 --max-emoji 3
```

Exit codes: `0` pass, `1` fail, `2` file or list could not be read. That makes it easy to use as a gate in a script or a git hook.

## Edit the lists

All phrases live in [`phrases.json`](phrases.json), grouped as `words`, `openers_closers`, `outreach`, `comment_cliches` and `structures`. Add a line to any list, or add a new list with its own name and it is checked too. `structures` entries are regular expressions.

Some words on the list are fine in the right sentence ("landscape" in a photo caption). Use `--allow` for those, or delete them from the JSON.

## Use it with Claude Code

Tell Claude to run the check before it shows you any copy. For example, add this to your `CLAUDE.md`:

```markdown
Before showing me any post, comment, caption or email, save it to a file and run
`python3 path/to/ai-phrase-checker/check.py <file>`. If it prints FAIL, rewrite the
flagged lines and run it again until it prints PASS.
```

## Limits

A pass doesn't mean a draft reads as human. The script only catches phrases and patterns on its list. It can't judge tone, facts or whether the draft says anything. Treat it as a first filter, then read the draft out loud.

## License

MIT
