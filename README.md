# Шаблон агентской разработки с DDD и автоматизацией

[![CI/CD](https://github.com/guility/agents_template/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/guility/agents_template/actions/workflows/ci-cd.yml)

Этот репозиторий — меташаблон для разработки приложений с помощью AI-агентов. Он задаёт единый процесс от требований до релиза, архитектурные правила, роли участников, проверки качества и заготовки для нескольких языков.

Шаблон можно использовать с OpenCode, OpenHands, Claude Code, ChatGPT Codex, Cursor и Pi. Основная точка входа для всех инструментов — файл [`AGENTS.md`](./AGENTS.md).

## Что входит в шаблон

- DDD и чистая архитектура со слоями `domain`, `application`, `infrastructure` и `interface`.
- Последовательный процесс: требования → архитектура → тесты → реализация → ревью → релиз.
- Инструкции для аналитика, архитектора, QA, разработчика, оркестратора и ревьюеров.
- Атомарные требования в `requirements/` и ADR в `docs/design/`.
- Unit, integration, e2e и мутационные тесты.
- Проверки сложности, безопасности, форматирования и трассируемости.
- GitHub Actions и GitLab CI.
- Языковые заготовки для Python, Node.js/TypeScript, Rust, Go и C#.

## Структура репозитория

```text
.
├── AGENTS.md                  # Общие обязательные правила для AI-агентов
├── agents/                    # Инструкции отдельных ролей
│   ├── analyst/
│   ├── architect/
│   ├── developer/
│   ├── orchestrator/
│   ├── qa/
│   └── reviewers/
├── best_practices/            # Практики требований, архитектуры, тестов и кода
├── requirements/              # Атомарные требования REQ-XXX
├── docs/design/               # ADR и дизайн-документы
├── contracts/                 # OpenAPI, Protobuf и другие контракты
├── templates/                 # Языковые заготовки
│   ├── python/
│   ├── nodejs/
│   ├── rust/
│   ├── go/
│   └── csharp/
├── scripts/                   # Bootstrap, CI, тестирование и анализ
├── .github/workflows/         # GitHub Actions
└── .gitlab/ci/                # GitLab CI
```

## Быстрый старт

### 1. Создайте проект из шаблона

Создайте новый репозиторий через кнопку **Use this template** на GitHub или клонируйте его:

```bash
git clone <repository-url> my-project
cd my-project
```

Все общие скрипты написаны для Bash. На Windows запускайте их из WSL или Git Bash.

### 2. Выберите языковую заготовку

Для знакомства с шаблоном можно работать прямо в соответствующем каталоге `templates/<language>`.

| Стек | Рабочий каталог | Установка | Основная проверка |
|---|---|---|---|
| Python | `templates/python` | `uv sync --all-extras` | `uv run pytest --cov=src --cov-branch --cov-fail-under=100` |
| Node.js/TypeScript | `templates/nodejs` | `pnpm install` | `pnpm test` |
| Rust | `templates/rust` | `cargo fetch` | `cargo test --lib` |
| Go | `templates/go` | `go mod download` | `go test ./...` |
| C# | `templates/csharp` | создать `.sln` и `.csproj` на основе заготовки | `dotnet test` |

Пример для Python:

```bash
cd templates/python
uv sync --all-extras
uv run pytest --cov=src --cov-branch --cov-fail-under=100
cd ../..
```

Для отдельного production-проекта перенесите содержимое выбранной заготовки в корень репозитория, удалите неиспользуемые языковые задания из CI и замените их рабочие каталоги на корень проекта. Это удобно поручить агенту отдельной задачей:

```text
Адаптируй этот меташаблон под Python-проект: перенеси templates/python в корень,
сохрани AGENTS.md, agents, best_practices и scripts, удали из CI задания других
языков и проверь локальные команды и GitHub Actions.
```

### 3. Подготовьте общие инструменты

Перед запуском изучите [`scripts/setup/bootstrap.sh`](./scripts/setup/bootstrap.sh): он устанавливает глобальные инструменты разработки и Git hooks. Если такое поведение подходит вашему окружению, выполните:

```bash
bash scripts/setup/bootstrap.sh
```

Хук также можно подключить вручную:

```bash
git config core.hooksPath scripts/hooks
```

### 4. Проверьте, что агент видит правила

Откройте репозиторий именно из его корня и начните с безопасного запроса без изменений:

```text
Не изменяй файлы. Изучи AGENTS.md, опиши обязательный workflow,
архитектурные ограничения, требования к тестам и команды проверок.
```

В ответе должны появиться DDD, чистая архитектура, последовательность этапов, обязательное чтение `best_practices/`, покрытие тестами и ограничение сложности не выше 10.

## Как устроена работа с агентами

Файлы в `agents/` являются инструкциями ролей, а не автоматически запущенными процессами. Поддерживаемые AI-инструменты загрузят общий `AGENTS.md`, но для конкретного этапа следует явно попросить прочитать файл нужной роли и соответствующий документ из `best_practices/`.

| Этап | Инструкция роли | Обязательный результат |
|---|---|---|
| Анализ | `agents/analyst/AGENT.md` | один файл `requirements/REQ-XXX.md` на требование |
| Проектирование | `agents/architect/AGENT.md` | ADR в `docs/design/`, модель и контракты |
| Подготовка тестов | `agents/qa/AGENT.md` | падающие тесты, описывающие ожидаемое поведение |
| Реализация | `agents/developer/AGENT.md` | код, проходящий согласованные тесты |
| Ревью | `agents/reviewers/*.md` | замечания либо подтверждение соответствия |
| Координация | `agents/orchestrator/AGENT.md` | контроль порядка этапов и возвратов |

Универсальный стартовый запрос для новой задачи:

```text
Изучи AGENTS.md и определи текущий этап workflow. Работай с кодом в
templates/python. Перед действиями прочитай инструкцию нужной роли и связанный
документ из best_practices. Не переходи к следующему этапу, пока артефакты
текущего этапа не готовы и не проверены. В конце перечисли изменённые файлы и
выполненные проверки.
```

Примеры запросов по этапам:

```text
# Требования
Работай как аналитик. Прочитай agents/analyst/AGENT.md и
best_practices/requirements_best_practices.md. Сформируй атомарное требование
REQ-001 с критериями Given-When-Then. Код пока не изменяй.

# Архитектура
Требование REQ-001 утверждено. Прочитай agents/architect/AGENT.md и
best_practices/architecture_best_practices.md. Подготовь ADR и контракты.
Реализацию не начинай.

# Тесты
Для утверждённых REQ-001 и ADR подготовь тесты по TDD. Прочитай
agents/qa/AGENT.md и best_practices/testing_best_practices.md. Покажи, что новые
тесты падают по ожидаемой причине.

# Реализация
Реализуй REQ-001 по утверждённому ADR и существующим падающим тестам. Прочитай
agents/developer/AGENT.md и best_practices/coding_best_practices.md. После
изменений запусти форматирование, линтер, тесты и анализ сложности.

# Ревью
Проведи ревью текущего diff по agents/reviewers/code_reviewer.md. Не изменяй
код. Сначала перечисли замечания по приоритету со ссылками на файлы и строки.
```

## Использование с OpenCode

[OpenCode](https://opencode.ai/docs/) автоматически ищет `AGENTS.md` в текущем каталоге и выше по дереву.

Установите OpenCode одним из способов, описанных в официальной документации. Например, через npm:

```bash
npm install -g opencode-ai
cd my-project
opencode
```

Дополнительная настройка шаблона не требуется. Не запускайте `/init`, если не хотите, чтобы OpenCode предложил изменить уже подготовленный `AGENTS.md`.

Первый запрос:

```text
Подтверди, что загрузил корневой AGENTS.md. Не изменяй файлы. Определи текущий
этап workflow и предложи следующий безопасный шаг.
```

Если нужны дополнительные инструкции, добавьте их в `opencode.json` через поле `instructions`, не дублируя содержимое `AGENTS.md`.

## Использование с OpenHands

[OpenHands](https://docs.openhands.dev/openhands/usage/cli/installation) использует корневой `AGENTS.md` как постоянный контекст репозитория.

Установка CLI через `uv`:

```bash
uv tool install openhands --python 3.12
cd my-project
openhands
```

На Windows OpenHands CLI следует запускать в WSL. При использовании OpenHands Cloud подключите репозиторий и убедитесь, что рабочая область открыта от его корня. Отдельный файл в `.openhands/` для чтения правил не нужен.

Запуск сразу с задачей:

```bash
openhands -t "Изучи AGENTS.md и проверь готовность проекта к этапу разработки"
```

Для специализированных процедур OpenHands можно дополнительно использовать `.agents/skills/<skill-name>/SKILL.md`, оставляя общие правила в `AGENTS.md`.

## Использование с Claude Code

[Claude Code](https://code.claude.com/docs/en/quickstart) автоматически читает `CLAUDE.md`, но не `AGENTS.md`. Создайте в корне проекта файл `CLAUDE.md` со следующим содержимым:

```markdown
@AGENTS.md
```

Так Claude Code будет использовать единый источник правил без копирования и рассинхронизации. При необходимости ниже импорта можно добавить только Claude-специфичные указания.

Запуск:

```bash
cd my-project
claude
```

Внутри сессии выполните `/context` и убедитесь, что `CLAUDE.md` присутствует среди загруженных файлов памяти. После этого используйте общий стартовый запрос из этого README.

На Windows импорт `@AGENTS.md` предпочтительнее символической ссылки: он не требует прав администратора или Developer Mode. Подробнее — в [официальной документации о памяти Claude Code](https://code.claude.com/docs/en/memory#agentsmd).

## Использование с ChatGPT Codex

[ChatGPT Codex](https://learn.chatgpt.com/docs/codex/cli) автоматически читает `AGENTS.md` до начала работы. Корневой файл уже подготовлен, поэтому `/init` запускать не нужно.

Установите Codex согласно официальной инструкции для своей платформы, откройте корень проекта и запустите:

```bash
cd my-project
codex
```

В Codex Desktop или IDE-расширении достаточно открыть папку репозитория как рабочую область. Для проверки контекста попросите:

```text
Не изменяй файлы. Перечисли инструкции, загруженные из AGENTS.md, и укажи,
какие файлы роли и best_practices нужно прочитать для реализации новой функции.
```

Codex объединяет инструкции от корня репозитория до текущего рабочего каталога. Если позже появятся вложенные `AGENTS.md`, более близкие к редактируемому коду правила должны уточнять, а не противоречить корневому файлу. Подробнее — в [официальной документации OpenAI по `AGENTS.md`](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Использование с Cursor

[Cursor](https://docs.cursor.com/context/rules-for-ai) поддерживает корневой `AGENTS.md` как простой вариант Project Rules. Дополнительный `.cursorrules` не нужен.

1. Откройте корень репозитория в Cursor.
2. В режиме **Ask** сначала запросите анализ проекта без изменений.
3. Для согласованной реализации переключитесь в **Agent** и передайте задачу вместе с нужным этапом workflow.
4. Перед применением проверьте diff и результаты тестов.

Пример запроса:

```text
Изучи AGENTS.md. Пока работай в режиме анализа: определи, какие требования и
ADR относятся к задаче, какие тесты потребуются и какой этап workflow сейчас
активен. Не изменяй файлы до согласования плана.
```

Cursor Agent можно использовать и из терминала:

```bash
curl https://cursor.com/install -fsS | bash
cd my-project
cursor-agent
```

CLI также читает корневой `AGENTS.md`. Для узких правил по каталогам или типам файлов можно дополнительно создать `.cursor/rules/*.mdc`; общие правила шаблона при этом оставляйте в `AGENTS.md`.

## Использование с Pi

[Pi](https://pi.dev/) загружает `AGENTS.md` при старте из текущего каталога, родительских каталогов и пользовательского каталога `~/.pi/agent/`.

Установка на Linux/macOS/WSL:

```bash
curl -fsSL https://pi.dev/install.sh | sh
```

Установка в PowerShell:

```powershell
powershell -c "irm https://pi.dev/install.ps1 | iex"
```

Запускайте Pi из корня проекта, чтобы область действия правил была однозначной:

```bash
cd my-project
pi
```

При первом запуске выберите провайдера и модель, затем проверьте контекст:

```text
Не изменяй файлы. Кратко перескажи корневой AGENTS.md и назови обязательные
артефакты этапов Analyst, Architect, QA и Developer.
```

Для этого шаблона не требуется отдельный `SYSTEM.md`: он заменяет или расширяет системный промпт Pi и нужен только для Pi-специфичного поведения.

## Полезные проверки

Проверка формата требований:

```bash
bash scripts/common/validate_requirements.sh
```

Проверка последовательности workflow:

```bash
bash scripts/common/check_workflow_status.sh
```

Анализ сложности выбранной заготовки:

```bash
python scripts/testing/complexity_analyzer.py \
  --root templates/python \
  --max-complexity 10 \
  --patterns '*.py'
```

Мутационное тестирование выбранной заготовки:

```bash
python scripts/testing/mutation_runner.py \
  --project-root templates/python \
  --language python \
  --generate-report
```

Матрица трассируемости:

```bash
python scripts/testing/traceability_matrix.py --root .
```

Полная пост-агентная валидация:

```bash
python scripts/validation/post_agent_validator.py --project-root .
```

GitHub Actions находится в `.github/workflows/ci-cd.yml`, GitLab CI подключается через корневой `.gitlab-ci.yml`. В текущем виде CI проверяет все языковые заготовки. После выбора одного стека адаптируйте pipeline под фактический корень приложения.

## Рекомендации по безопасной работе

- Запускайте агента из корня репозитория и проверяйте, какие инструкции он загрузил.
- Начинайте крупные задачи с режима анализа или плана.
- Не включайте безусловное автоматическое подтверждение команд для незнакомого репозитория.
- Не передавайте ключи и токены в запросах и не сохраняйте их в Git.
- Просматривайте `git diff` после каждого этапа.
- Не разрешайте переход к реализации без утверждённых требований, ADR и тестов.
- Перед коммитом запускайте проверки выбранного стека и pre-commit hook.
- Не просите агента одновременно менять требования, архитектуру и реализацию без явного решения оркестратора.

## Официальная документация интеграций

- [OpenCode: правила и `AGENTS.md`](https://opencode.ai/docs/rules/)
- [OpenHands: Skills и постоянный контекст](https://docs.openhands.dev/overview/skills)
- [Claude Code: `CLAUDE.md` и импорт `AGENTS.md`](https://code.claude.com/docs/en/memory#agentsmd)
- [ChatGPT Codex: CLI](https://learn.chatgpt.com/docs/codex/cli)
- [ChatGPT Codex: инструкции `AGENTS.md`](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Cursor: Project Rules и `AGENTS.md`](https://docs.cursor.com/context/rules-for-ai)
- [Pi: установка и контекст проекта](https://pi.dev/)

## Лицензия

Перед публикацией проекта добавьте подходящий файл лицензии. Для открытых производных проектов можно использовать MIT License.
