# 🎨 **RecifeMais - Design System & Guia de Estilo**

### *Portal Cultural & Noticioso - Inspirado nas melhores práticas da Globo.com*

---

## 📋 **Índice**

1. **[Filosofia de Design](#filosofia-de-design)**
2. **[Paleta de Cores](#paleta-de-cores)**
3. **[Tipografia](#tipografia)**
4. **[Layout & Grid](#layout--grid)**
5. **[Componentes](#componentes)**
6. **[Hierarquia Visual](#hierarquia-visual)**
7. **[Responsividade](#responsividade)**
8. **[Acessibilidade](#acessibilidade)**

---

## 🎯 **Filosofia de Design**

### **Conceito Central: "Jornalismo Elegante"**
Inspirado na **Globo.com**, nosso design prioriza:

- **Legibilidade acima de tudo** - Conteúdo é rei
- **Hierarquia visual clara** - Informação organizada
- **Elegância discreta** - Sofisticação sem ostentação
- **Cores estratégicas** - Destaques pontuais, não dominantes
- **Background neutro** - Tons de cinza como base

### **Princípios Fundamentais:**

1. **📰 Jornalístico** - Layout limpo, informação clara
2. **🎨 Cultural** - Toques de cor que remetem à cultura pernambucana
3. **📱 Responsivo** - Mobile-first, desktop-enhanced
4. **⚡ Performance** - Carregamento rápido, UX fluida
5. **♿ Acessível** - Inclusivo para todos os usuários

---

## 🎨 **Paleta de Cores**

### **🔴 Cores Primárias (Uso Estratégico)**
```css
:root {
  /* Vermelho RecifeMais - Cor principal */
  --recife-primary: #e11d48;
  --recife-primary-dark: #be123c;
  --recife-primary-light: #f43f5e;
  
  /* Laranja Energia - Cor secundária */
  --recife-secondary: #ff6b35;
  --recife-secondary-dark: #ea580c;
  --recife-secondary-light: #fb923c;
}
```

### **🌊 Cores de Apoio (Destaques Pontuais)**
```css
:root {
  /* Azul Oceano - Links e elementos interativos */
  --recife-accent: #0ea5e9;
  --recife-accent-dark: #0284c7;
  --recife-accent-light: #38bdf8;
  
  /* Verde Mangue - Sucesso e natureza */
  --recife-success: #10b981;
  
  /* Roxo Criativo - Arte e cultura */
  --recife-creative: #8b5cf6;
  
  /* Amarelo Solar - Alertas e destaques */
  --recife-warning: #f59e0b;
}
```

### **⚫ Tons de Cinza (Base Dominante)**
```css
:root {
  /* Escala de cinzas - Inspirada na Globo.com */
  --recife-gray-50: #f9fafb;   /* Background principal */
  --recife-gray-100: #f3f4f6;  /* Background cards */
  --recife-gray-200: #e5e7eb;  /* Bordas sutis */
  --recife-gray-300: #d1d5db;  /* Bordas visíveis */
  --recife-gray-400: #9ca3af;  /* Texto secundário */
  --recife-gray-500: #6b7280;  /* Texto terciário */
  --recife-gray-600: #4b5563;  /* Texto normal */
  --recife-gray-700: #374151;  /* Texto principal */
  --recife-gray-800: #1f2937;  /* Títulos */
  --recife-gray-900: #111827;  /* Títulos principais */
}
```

### **🎭 Cores por Seção (CPTs)**
```css
:root {
  /* Cores específicas para cada tipo de conteúdo */
  --cpt-eventos: #e11d48;      /* Vermelho - Eventos */
  --cpt-lugares: #0ea5e9;      /* Azul - Lugares */
  --cpt-artistas: #8b5cf6;     /* Roxo - Artistas */
  --cpt-organizadores: #f59e0b; /* Amarelo - Organizadores */
  --cpt-roteiros: #ff6b35;     /* Laranja - Roteiros */
  --cpt-agremiacoes: #10b981;  /* Verde - Agremiações */
  --cpt-historias: #6366f1;    /* Índigo - Histórias */
  --cpt-guias: #ec4899;        /* Rosa - Guias */
}
```

### **📊 Uso das Cores (Regras Rígidas)**

#### **✅ PERMITIDO:**
- **Background:** Sempre tons de cinza (gray-50 a gray-100)
- **Texto principal:** Cinza escuro (gray-700 a gray-900)
- **Destaques pontuais:** Cores primárias em títulos, badges, botões
- **Links:** Azul accent ou vermelho primary
- **Estados:** Verde (sucesso), vermelho (erro), amarelo (aviso)

#### **❌ PROIBIDO:**
- Backgrounds coloridos dominantes
- Texto colorido em parágrafos longos
- Múltiplas cores na mesma seção
- Cores saturadas em grandes áreas
- Gradientes chamativos

---

## ✍️ **Tipografia**

### **📝 Fonte Principal: Inter**
```css
body {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 
               'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-feature-settings: "cv02", "cv03", "cv04", "cv11";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### **📏 Escala Tipográfica (Inspirada na Globo)**

#### **🏆 Headlines (Manchetes)**
```css
/* Display XL - Manchetes principais */
.headline-display {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--recife-gray-900);
}

/* Headline XL - Títulos de seção */
.headline-xl {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--recife-gray-800);
}

/* Headline LG - Subtítulos importantes */
.headline-lg {
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  font-weight: 600;
  line-height: 1.3;
  color: var(--recife-gray-800);
}
```

#### **📰 Títulos de Conteúdo**
```css
/* H1 - Título principal da página */
h1 {
  font-size: clamp(1.875rem, 3vw, 2.5rem);
  font-weight: 700;
  line-height: 1.25;
  color: var(--recife-gray-900);
  margin-bottom: 1rem;
}

/* H2 - Títulos de seção */
h2 {
  font-size: clamp(1.5rem, 2.5vw, 2rem);
  font-weight: 600;
  line-height: 1.3;
  color: var(--recife-gray-800);
  margin-top: 2rem;
  margin-bottom: 1rem;
}

/* H3 - Subtítulos */
h3 {
  font-size: clamp(1.25rem, 2vw, 1.5rem);
  font-weight: 600;
  line-height: 1.4;
  color: var(--recife-gray-700);
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

/* H4 - Títulos menores */
h4 {
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.5;
  color: var(--recife-gray-700);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}
```

#### **📄 Texto Corrido**
```css
/* Parágrafo principal */
p {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--recife-gray-700);
  margin-bottom: 1.25rem;
}

/* Lead text - Primeiro parágrafo */
.lead {
  font-size: 1.125rem;
  line-height: 1.6;
  color: var(--recife-gray-600);
  font-weight: 400;
}

/* Texto pequeno */
.text-small {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--recife-gray-600);
}

/* Caption - Legendas */
.caption {
  font-size: 0.75rem;
  line-height: 1.4;
  color: var(--recife-gray-500);
  font-weight: 500;
}
```

### **🎯 Hierarquia de Peso**
```css
/* Pesos específicos por contexto */
.font-light { font-weight: 300; }    /* Textos longos */
.font-normal { font-weight: 400; }   /* Texto padrão */
.font-medium { font-weight: 500; }   /* Destaques sutis */
.font-semibold { font-weight: 600; } /* Títulos menores */
.font-bold { font-weight: 700; }     /* Títulos principais */
.font-extrabold { font-weight: 800; } /* Manchetes */
```

---

## 📐 **Layout & Grid**

### **🏗️ Container System**
```css
/* Container responsivo - Inspirado na Globo */
.container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (min-width: 640px) {
  .container { padding: 0 1.5rem; }
}

@media (min-width: 1024px) {
  .container { padding: 0 2rem; }
}

@media (min-width: 1280px) {
  .container { padding: 0 2.5rem; }
}
```

### **📱 Breakpoints**
```css
/* Mobile First - Breakpoints estratégicos */
:root {
  --bp-sm: 640px;   /* Tablet pequeno */
  --bp-md: 768px;   /* Tablet */
  --bp-lg: 1024px;  /* Desktop */
  --bp-xl: 1280px;  /* Desktop grande */
  --bp-2xl: 1536px; /* Desktop extra */
}
```

### **🎯 Grid System (12 colunas)**
```css
/* Grid principal - Flexível como Globo.com */
.grid-main {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.5rem;
}

/* Layout típico de portal */
.layout-portal {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
}

@media (max-width: 1023px) {
  .layout-portal {
    grid-template-columns: 1fr;
  }
}
```

### **📏 Espaçamento Consistente**
```css
/* Sistema de espaçamento baseado em 4px */
:root {
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */
  --space-20: 5rem;    /* 80px */
}
```

---

## 🧩 **Componentes**

### **📰 Cards (Estilo Globo)**

#### **Card Principal**
```css
.card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 2px 15px -3px rgba(0, 0, 0, 0.07), 
              0 10px 20px -2px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  overflow: hidden;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 
              0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
```

#### **Card Hero (Destaque Principal)**
```css
.card-hero {
  position: relative;
  aspect-ratio: 16/9;
  background: linear-gradient(
    135deg, 
    rgba(0, 0, 0, 0.6) 0%, 
    rgba(0, 0, 0, 0.3) 100%
  );
  border-radius: 1rem;
  overflow: hidden;
}

.card-hero-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 2rem;
  color: white;
}

.card-hero-title {
  font-size: clamp(1.5rem, 3vw, 2.5rem);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 0.5rem;
}
```

#### **Card Horizontal (Lista)**
```css
.card-horizontal {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s ease;
}

.card-horizontal:hover {
  background-color: var(--recife-gray-50);
}

.card-horizontal-image {
  width: 80px;
  height: 80px;
  border-radius: 0.5rem;
  object-fit: cover;
  flex-shrink: 0;
}
```

### **🔘 Botões (Hierarquia Clara)**

#### **Botão Primário**
```css
.btn-primary {
  background: var(--recife-primary);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--recife-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px 0 rgba(225, 29, 72, 0.25);
}
```

#### **Botão Secundário**
```css
.btn-secondary {
  background: transparent;
  color: var(--recife-primary);
  border: 2px solid var(--recife-primary);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.btn-secondary:hover {
  background: var(--recife-primary);
  color: white;
}
```

#### **Botão Ghost**
```css
.btn-ghost {
  background: transparent;
  color: var(--recife-gray-700);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.btn-ghost:hover {
  background: var(--recife-gray-100);
  color: var(--recife-gray-900);
}
```

### **🏷️ Badges (Categorização)**
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

/* Badges por categoria */
.badge-eventos {
  background: var(--cpt-eventos);
  color: white;
}

.badge-lugares {
  background: var(--cpt-lugares);
  color: white;
}

.badge-artistas {
  background: var(--cpt-artistas);
  color: white;
}
```

### **📝 Formulários (Limpos e Funcionais)**
```css
.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid var(--recife-gray-200);
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: var(--recife-primary);
  box-shadow: 0 0 0 3px rgba(225, 29, 72, 0.1);
}

.form-label {
  display: block;
  font-weight: 600;
  color: var(--recife-gray-700);
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}
```

---

## 📊 **Hierarquia Visual**

### **🎯 Prioridades de Informação**

#### **Nível 1 - Crítico (Vermelho Primary)**
- Manchetes principais
- CTAs importantes
- Alertas críticos
- Breaking news

#### **Nível 2 - Importante (Cinza Escuro)**
- Títulos de seção
- Navegação principal
- Informações essenciais

#### **Nível 3 - Secundário (Cinza Médio)**
- Texto corrido
- Metadados
- Navegação secundária

#### **Nível 4 - Terciário (Cinza Claro)**
- Informações auxiliares
- Timestamps
- Créditos

### **📐 Espaçamento Hierárquico**
```css
/* Espaçamentos por importância */
.spacing-critical { margin-bottom: 3rem; }    /* Seções principais */
.spacing-important { margin-bottom: 2rem; }   /* Subsections */
.spacing-normal { margin-bottom: 1.5rem; }    /* Parágrafos */
.spacing-small { margin-bottom: 1rem; }       /* Elementos menores */
.spacing-tiny { margin-bottom: 0.5rem; }      /* Detalhes */
```

---

## 📱 **Responsividade**

### **🎯 Estratégia Mobile-First**

#### **Mobile (320px - 767px)**
```css
/* Layout mobile - Stack vertical */
.mobile-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Tipografia mobile */
.mobile-text {
  font-size: 0.875rem;
  line-height: 1.6;
}

/* Cards mobile */
.mobile-card {
  margin-bottom: 1rem;
  border-radius: 0.5rem;
}
```

#### **Tablet (768px - 1023px)**
```css
/* Layout tablet - Grid 2 colunas */
@media (min-width: 768px) {
  .tablet-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}
```

#### **Desktop (1024px+)**
```css
/* Layout desktop - Grid completo */
@media (min-width: 1024px) {
  .desktop-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }
  
  .desktop-sidebar {
    grid-template-columns: 1fr 300px;
  }
}
```

### **🖼️ Imagens Responsivas**
```css
/* Sistema de imagens adaptáveis */
.responsive-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 0.5rem;
}

/* Aspect ratios por contexto */
.aspect-hero { aspect-ratio: 16/9; }
.aspect-card { aspect-ratio: 4/3; }
.aspect-thumb { aspect-ratio: 1/1; }
```

---

## ♿ **Acessibilidade**

### **🎯 Contraste e Legibilidade**
```css
/* Contrastes mínimos WCAG 2.1 AA */
:root {
  --contrast-normal: 4.5;   /* Texto normal */
  --contrast-large: 3.0;    /* Texto grande */
  --contrast-ui: 3.0;       /* Elementos UI */
}

/* Estados de foco visíveis */
.focus-visible:focus {
  outline: 2px solid var(--recife-primary);
  outline-offset: 2px;
  border-radius: 0.25rem;
}
```

### **📱 Navegação por Teclado**
```css
/* Skip links */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--recife-primary);
  color: white;
  padding: 8px;
  text-decoration: none;
  border-radius: 0.25rem;
  z-index: 1000;
}

.skip-link:focus {
  top: 6px;
}
```

### **🔊 Screen Readers**
```css
/* Texto apenas para screen readers */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## 🎨 **Implementação CSS**

### **🔧 Variáveis CSS Completas**
```css
:root {
  /* === CORES === */
  /* Primárias */
  --recife-primary: #e11d48;
  --recife-primary-dark: #be123c;
  --recife-primary-light: #f43f5e;
  --recife-secondary: #ff6b35;
  --recife-accent: #0ea5e9;
  
  /* Escala de cinzas */
  --recife-gray-50: #f9fafb;
  --recife-gray-100: #f3f4f6;
  --recife-gray-200: #e5e7eb;
  --recife-gray-300: #d1d5db;
  --recife-gray-400: #9ca3af;
  --recife-gray-500: #6b7280;
  --recife-gray-600: #4b5563;
  --recife-gray-700: #374151;
  --recife-gray-800: #1f2937;
  --recife-gray-900: #111827;
  
  /* === TIPOGRAFIA === */
  --font-family-base: 'Inter', system-ui, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  
  /* === ESPAÇAMENTO === */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  
  /* === SOMBRAS === */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  
  /* === TRANSIÇÕES === */
  --transition-fast: all 0.2s ease;
  --transition-base: all 0.3s ease;
  --transition-slow: all 0.5s ease;
  
  /* === BORDAS === */
  --border-radius-sm: 0.25rem;
  --border-radius-md: 0.5rem;
  --border-radius-lg: 0.75rem;
  --border-radius-xl: 1rem;
  --border-radius-full: 9999px;
}
```