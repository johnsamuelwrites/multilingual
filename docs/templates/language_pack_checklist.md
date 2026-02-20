# Language Pack PR Checklist

Language code: `xx`

- [ ] Added language code to `multilingualprogramming/resources/usm/keywords.json`.
- [ ] Added all keyword concept translations for the language.
- [ ] Verified no new keyword ambiguities.
- [ ] Added parser/semantic messages in `multilingualprogramming/resources/parser/error_messages.json`.
- [ ] Added REPL help/messages/aliases in `multilingualprogramming/resources/repl/commands.json`.
- [ ] Added or reviewed built-in aliases in `multilingualprogramming/resources/usm/builtins_aliases.json` (optional).
- [ ] Added surface patterns in `multilingualprogramming/resources/usm/surface_patterns.json` (optional).
- [ ] Added tests for keyword registry, executor, and error messages.
- [ ] Ran `python -m multilingualprogramming smoke --lang xx`.
- [ ] Ran `python -m pytest -q` and `python -m pylint $(git ls-files '*.py')`.
