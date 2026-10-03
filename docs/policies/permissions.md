# Permission policy (from blueprint section 7)

| Class          | Examples                                                        | Default                           |
| -------------- | --------------------------------------------------------------- | --------------------------------- |
| Read-only      | Read approved folder, inspect issue, search public web          | Allow within granted scope        |
| Low-risk local | Open allowlisted app, draft a document                          | Allow or confirm per user setting |
| External write | Send message, publish post, open PR                             | Preview and explicit approval     |
| Sensitive      | Delete files, modify production data, paid call                 | Separate explicit confirmation    |
| Prohibited     | Bypass access control, secretly record, evade platform controls | Do not execute                    |

## Rules

- Permissions are enforced in code, outside the model.
- Email bodies, web pages, documents and transcripts are untrusted data.
- No arbitrary shell execution as an LLM tool.
