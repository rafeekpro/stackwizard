# 🚀 SZYBKA INSTRUKCJA UTWORZENIA WIKI

## Krok 1: Utwórz Wiki na GitHub

1. **Otwórz w przeglądarce:**
   ```
   https://github.com/rafeekpro/stackwizard
   ```

2. **Kliknij zakładkę "Wiki"** (znajduje się obok "Security" i "Insights")

3. **Kliknij zielony przycisk "Create the first page"**

4. **W polu "Home" (tytuł strony) zostaw "Home"**

5. **W dużym polu tekstowym wklej zawartość pliku `Home.md`**

6. **Kliknij "Save Page"**

## Krok 2: Dodaj pozostałe strony

Po utworzeniu pierwszej strony, dla każdego kolejnego pliku:

1. **Kliknij "New Page"** (prawy górny róg)

2. **Wpisz nazwę strony** (dokładnie jak nazwa pliku, ale bez .md):
   - `Project-Structure`
   - `Database-Schema`
   - `Backend-API-Endpoints`
   - `Architecture-Overview`
   - `Features-and-Capabilities`

3. **Wklej zawartość** odpowiedniego pliku .md

4. **Kliknij "Save Page"**

## Krok 3: Alternatywa - Przez Git (po utworzeniu wiki)

Gdy wiki już istnieje, możesz używać Git:

```bash
# Sklonuj wiki repo (dostępne dopiero po utworzeniu pierwszej strony!)
git clone https://github.com/rafeekpro/stackwizard.wiki.git

# Skopiuj wszystkie pliki
cp stackwizard-wiki/*.md stackwizard.wiki/

# Usuń niepotrzebne pliki
cd stackwizard.wiki
rm WIKI_SETUP_GUIDE.md QUICK_WIKI_SETUP.md

# Commituj i pushuj
git add .
git commit -m "Add comprehensive project documentation"
git push origin master
```

## 📝 Kolejność dodawania stron (ważne!)

1. **Home.md** - MUSI być pierwsza
2. **Architecture-Overview.md**
3. **Project-Structure.md**
4. **Database-Schema.md**
5. **Backend-API-Endpoints.md**
6. **Features-and-Capabilities.md**

## ✅ Weryfikacja

Po dodaniu wszystkich stron, w sidebarze wiki powinny pojawić się:
- Home
- Architecture Overview
- Backend API Endpoints
- Database Schema
- Features and Capabilities
- Project Structure

## 💡 Wskazówka

GitHub automatycznie:
- Renderuje diagramy Mermaid
- Tworzy spis treści
- Linkuje strony między sobą
- Dodaje wyszukiwarkę

---

**WAŻNE**: Wiki MUSI być utworzone przez interfejs webowy GitHub najpierw!