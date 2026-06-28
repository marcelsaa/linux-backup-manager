# Internationalization

**Version:** 1.1.0-dev

## Scope

Sprint 38 provides the internationalization infrastructure. It does not translate every existing
command yet. German remains the default for configurations created before this sprint.

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

Future sprints will migrate CLI messages to catalog keys in small, testable groups and later
provide complete German and English user documentation.
