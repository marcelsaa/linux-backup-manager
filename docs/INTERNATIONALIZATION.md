# Internationalization

**Version:** 1.1.0-dev

## Scope

Sprint 38 provided the infrastructure. Sprint 39 migrated the complete user-facing output of
`status`, `doctor`, `health` and `setup`, including target-resolution and scheduler messages used by
those workflows. German remains the default for configurations created before Sprint 38.

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

## Next Steps

The following command groups remain to be migrated:

* backup, restore, snapshots, stats, check, forget and prune;
* recovery-info and recovery-sheet;
* standalone schedule commands and remaining shared error messages.

Complete German and English user documentation remains a later milestone.
