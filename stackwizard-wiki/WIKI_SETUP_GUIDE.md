# 📖 GitHub Wiki Setup Guide

## Jak dodać dokumentację do GitHub Wiki

### Metoda 1: Przez interfejs GitHub (Zalecana)

1. **Przejdź do repozytorium**
   ```
   https://github.com/rafeekpro/stackwizard
   ```

2. **Kliknij zakładkę "Wiki"** w górnym menu

3. **Kliknij "Create the first page"** jeśli wiki nie istnieje

4. **Dla każdego pliku .md w folderze stackwizard-wiki:**
   - Kliknij "New Page"
   - Skopiuj nazwę pliku (bez .md) jako tytuł strony
   - Skopiuj zawartość pliku do edytora
   - Kliknij "Save Page"

### Metoda 2: Przez Git (Dla zaawansowanych)

1. **Sklonuj wiki repozytorium**
   ```bash
   git clone https://github.com/rafeekpro/stackwizard.wiki.git
   ```

2. **Skopiuj pliki dokumentacji**
   ```bash
   cp stackwizard-wiki/*.md stackwizard.wiki/
   ```

3. **Commituj i pushuj zmiany**
   ```bash
   cd stackwizard.wiki
   git add .
   git commit -m "Add comprehensive project documentation"
   git push origin master
   ```

## 📁 Struktura dokumentacji

```
stackwizard-wiki/
├── Home.md                      # Strona główna wiki
├── Project-Structure.md         # Struktura projektu
├── Database-Schema.md          # Schemat bazy danych
├── Backend-API-Endpoints.md    # Dokumentacja API
├── Architecture-Overview.md    # Przegląd architektury
└── Features-and-Capabilities.md # Funkcje i możliwości
```

## 🎯 Zalety posiadania wiki

1. **Profesjonalizm** - Pokazuje, że projekt jest dobrze udokumentowany
2. **Łatwa nawigacja** - GitHub automatycznie tworzy menu boczne
3. **Wersjonowanie** - Historia zmian dokumentacji
4. **Markdown support** - Wsparcie dla diagramów Mermaid
5. **Searchable** - Możliwość wyszukiwania w dokumentacji
6. **No extra setup** - Nie wymaga dodatkowych narzędzi

## 🔗 Linki w README

Po dodaniu wiki, zaktualizuj README.md dodając link:

```markdown
## 📚 Documentation

For detailed documentation, visit our [GitHub Wiki](https://github.com/rafeekpro/stackwizard/wiki)
```

## 💡 Wskazówki

- Używaj diagramów Mermaid - GitHub renderuje je automatycznie
- Dodawaj linki między stronami wiki dla łatwej nawigacji
- Regularnie aktualizuj dokumentację wraz z rozwojem projektu
- Dodaj screenshoty dla lepszej wizualizacji

---

**Autor**: Rafał Łagowski | [GitHub](https://github.com/rafeekpro)