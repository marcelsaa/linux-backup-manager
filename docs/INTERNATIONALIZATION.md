# Internationalization

**Version:** 1.3.1

## Scope

Sprint 38 provided the infrastructure, Sprint 39 migrated the four central interactive workflows,
and Sprint 40 completed the remaining command groups. All application-generated CLI output now
uses the selected language. German remains the default for configurations created before Sprint 38.

## Language Configuration

The selected language is stored in `config.yaml`:

```yaml
system:
  host_name: blackpanther
  language: de
```

Supported values are `de` and `en`. The setup wizard asks for the language when creating or
editing a configuration. Existing configurations without `system.language` automatically use
`de` and remain valid.

## Language Service

`LanguageService` is the central interface for translated application messages:

```python
from lbm.services.language import LanguageService

language = LanguageService("en")
message = language.translate("language.selected", language="en")
```

Catalogs are YAML files in `src/lbm/resources/i18n/` and are included in wheel and source
distributions.

## Fallback Order

Messages are resolved in this order:

1. selected language;
2. English;
3. German;
4. stable message key when no catalog contains the key.

An unsupported language passed directly to `LanguageService` falls back to English. Configuration
validation only accepts `de` and `en`, preventing misspelled persisted values.

## Completed CLI Scope

The translated command surface includes setup, status, health, doctor, backup, restore, snapshot
and repository maintenance, recovery information and sheets, due checks, scheduler actions and CLI
help. Generated recovery-sheet content follows the selected language as well.

Raw Restic and systemctl output remains unchanged because it belongs to those external programs.
Complete German and English long-form user documentation remains a later milestone.
