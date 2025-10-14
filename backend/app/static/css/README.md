# WaveBulk Frontend Architecture

## 📁 CSS Structure

Nowa architektura CSS oparta jest na modularnym podejściu, które zapewnia:
- ✅ Łatwość w utrzymaniu
- ✅ Możliwość ponownego wykorzystania
- ✅ Spójność wizualną
- ✅ Skalowalność

### Struktura plików

```
static/css/
├── base.css                    # Główny plik importujący wszystkie moduły
├── variables.css               # Zmienne CSS (design system)
├── utilities.css               # Klasy utility (Tailwind-like)
├── layout.css                  # Layout, header, footer, containers
└── components/                 # Komponenty UI
    ├── buttons.css            # Przyciski i ich warianty
    ├── forms.css              # Formularze, inputy, selecty
    ├── cards.css              # Karty (auth, feature, pricing, file)
    ├── tables.css             # Tabele i badge'e
    ├── alerts.css             # Alerty i komunikaty
    ├── upload.css             # Komponenty upload/drop-area
    ├── hero.css               # Sekcje hero i features
    └── google-button.css      # Przycisk logowania Google
```

## 🎨 Design System (variables.css)

### Kolory

```css
--bg-dark: #121212           /* Główne tło */
--bg-light: #1E1E1E         /* Jaśniejsze tło */
--bg-lighter: #282828       /* Jeszcze jaśniejsze */
--accent-color: #007BFF     /* Kolor akcji */
--text-primary: #FFFFFF     /* Główny tekst */
--text-secondary: #A0A0A0   /* Drugorzędny tekst */
```

### Spacing

```css
--spacing-xs: 0.25rem   (4px)
--spacing-sm: 0.5rem    (8px)
--spacing-md: 1rem      (16px)
--spacing-lg: 1.5rem    (24px)
--spacing-xl: 2rem      (32px)
--spacing-2xl: 2.5rem   (40px)
--spacing-3xl: 3rem     (48px)
```

### Typography

```css
--font-size-xs: 0.75rem    (12px)
--font-size-sm: 0.875rem   (14px)
--font-size-base: 1rem     (16px)
--font-size-lg: 1.125rem   (18px)
--font-size-xl: 1.25rem    (20px)
--font-size-2xl: 1.5rem    (24px)
--font-size-3xl: 2rem      (32px)
--font-size-4xl: 2.5rem    (40px)
--font-size-5xl: 3.5rem    (56px)
```

### Border Radius

```css
--radius-sm: 4px
--radius-md: 8px
--radius-lg: 12px
--radius-xl: 16px
--radius-full: 9999px
```

## 🛠️ Utility Classes

Zestaw klas utility wzorowany na Tailwind CSS:

### Display & Flexbox
```html
<div class="d-flex justify-center align-center gap-2">
```

### Spacing
```html
<div class="mt-4 mb-3 px-2 py-3">
```

### Typography
```html
<p class="text-lg text-secondary font-semibold">
```

### Width & Max-Width
```html
<div class="w-100 max-w-md mx-auto">
```

## 🧩 Komponenty

### Buttons

```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>
<button class="btn btn-primary btn-lg">Large Button</button>
<button class="btn btn-success btn-sm">Small Success</button>
```

### Forms

```html
<div class="form-group">
    <label for="email">Email</label>
    <input type="email" id="email" class="form-input">
</div>

<div class="form-group">
    <label>Select</label>
    <div class="custom-select">
        <select>
            <option>Option 1</option>
        </select>
    </div>
</div>
```

### Cards

```html
<!-- Auth Card -->
<div class="auth-card">
    <div class="auth-header">
        <div class="logo">WaveBulk</div>
        <h1>Welcome</h1>
    </div>
    <!-- Content -->
</div>

<!-- Feature Card -->
<div class="feature-card">
    <div class="icon">...</div>
    <h3>Title</h3>
    <p>Description</p>
</div>

<!-- Pricing Card -->
<div class="pricing-card">
    <h2 class="plan-name">Pro</h2>
    <div class="plan-price">49 zł <span>/ miesiąc</span></div>
    <p class="plan-description">Description</p>
    <a href="#" class="btn btn-primary btn-cta">Choose Plan</a>
</div>
```

### Tables

```html
<div class="table-responsive">
    <table class="table table-dark table-striped">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Data 1</td>
                <td><span class="badge bg-success">Success</span></td>
            </tr>
        </tbody>
    </table>
</div>
```

### Alerts

```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-danger">Error message</div>
<div class="alert alert-warning">Warning message</div>
```

## 📱 Responsywność

Breakpointy (dla referencji w media queries):

```css
--breakpoint-sm: 640px
--breakpoint-md: 768px
--breakpoint-lg: 1024px
--breakpoint-xl: 1280px
--breakpoint-2xl: 1536px
```

Zaimplementowane media queries:
- Mobile-first approach
- Ukrywanie nawigacji na małych ekranach (<768px)
- Responsywne gridy dla kart i funkcji
- Dostosowane rozmiary czcionek dla urządzeń mobilnych

## 📝 Najlepsze praktyki

1. **Używaj zmiennych CSS** zamiast hardcoded wartości
2. **Wykorzystuj utility classes** dla prostych stylów
3. **Twórz nowe komponenty** dla powtarzalnych elementów
4. **Zachowaj spójność** z istniejącym design system
5. **Mobile-first** - projektuj najpierw dla małych ekranów
6. **Testuj responsywność** na różnych rozdzielczościach

## 🔄 Migracja ze starego kodu

### Przed (inline styles):
```html
<div style="background-color: var(--bg-light); padding: 2rem; border-radius: 12px;">
```

### Po (utility classes):
```html
<div class="bg-light p-4 rounded-lg">
```

### Przed (duplikacja CSS):
```css
.component-a { background: var(--bg-light); padding: 1rem; }
.component-b { background: var(--bg-light); padding: 1rem; }
```

### Po (reusable component):
```css
.card { background: var(--bg-light); padding: 1rem; }
```

## 🎯 Przyszłe ulepszenia

- [ ] Dark/Light mode toggle
- [ ] Więcej wariantów kolorystycznych
- [ ] Animacje i transitions library
- [ ] Print styles optimization
- [ ] RTL (Right-to-Left) support
- [ ] Accessibility improvements (ARIA, focus styles)

