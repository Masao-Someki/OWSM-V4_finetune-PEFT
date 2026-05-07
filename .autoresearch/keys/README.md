# Keys Directory

Put local secret files here (one line per file, no quotes).

`*.key` files are gitignored by repository policy.

## Supported files
- `wandb.key` -> `WANDB_API_KEY`
- `wandb_entity.key` -> `WANDB_ENTITY`
- `wandb_project.key` -> `WANDB_PROJECT`
- `slack_webhook.key` -> `SLACK_WEBHOOK_URL`
- `openai_api.key` -> `OPENAI_API_KEY`
- `anthropic_api.key` -> `ANTHROPIC_API_KEY`  (Claude API、ローカルテスト用)
- `hf_token.key` -> `HF_TOKEN`

## GitHub Actions での Keys 管理

Cluster の `keys/` はローカル専用 (gitignore済み)。
GitHub Actions では以下を Secrets に登録する:

| Secret | 用途 |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API (autoresearch.yml で使用) |
| `SLACK_WEBHOOK_URL` | Slack 通知 (任意) |

## Notes
- Environment variables already set in shell take precedence over files.
- Backward compatibility is kept for legacy root files:
  - `wandb.key`
  - `wandb_entity.key`
  - `wandb_entry.key`
