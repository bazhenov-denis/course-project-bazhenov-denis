# EVIDENCE/P09

Структура для P09 — SBOM & SCA evidence.

Файлы:
- sbom.json            — SBOM (Syft), генерация в CI.
- sca_report.json      — SCA (Grype/Trivy) в формате json.
- sca_summary.md       — Краткая агрегированная сводка по severity и рекомендациям.

Генерация:
- CI workflow: .github/workflows/p09-sbom-sca.yml
- Артефакты хранятся в Actions artifacts (p09-evidence-${{ github.sha }}).
- При необходимости включается автоматический commit (COMMIT_SBOM=true) — тогда файлы попадают также в репозиторий.

Связь с PR:
- В PR просьба добавить ссылку на run (Actions -> run) и на имя артефакта p09-evidence-${{ github.sha }}.
