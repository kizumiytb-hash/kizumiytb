# ForexPro Trader - Site Web & Application de Trading

## 🌐 Structure du Projet

```
ForexPro Trader/
├── landing/              # Site web marketing
│   └── index.html       # Landing page
├── backend/             # API FastAPI
├── frontend/            # Application React de trading
└── README.md           # Ce fichier
```

## 🚀 Déploiement

### Site Web (Landing Page)
- **Fichier** : `/landing/index.html`
- **Hébergement recommandé** : Netlify, Vercel, GitHub Pages
- **URL de production** : `votre-domaine.com`

### Application de Trading
- **Backend** : FastAPI + MongoDB + Stripe LIVE
- **Frontend** : React + Authentification JWT
- **URL actuelle** : `https://19d7651f-4e24-4d23-ad4f-0ab1b902f33c.preview.emergentagent.com`

## 📄 Pages du Site Web

### Landing Page (`/landing/index.html`)
✅ **Hero Section** - Présentation ForexPro Trader
✅ **Statistiques** - Levier ∞, Spreads 0 pip, Frais 0%  
✅ **Fonctionnalités** - 6 fonctionnalités clés avec icônes
✅ **Call-to-Action** - Boutons vers l'application de trading
✅ **Footer** - Contact, sécurité, mentions légales
✅ **Design Responsive** - Compatible mobile/desktop
✅ **Animations** - Effets de survol et transitions

### Redirection vers l'App
Tous les boutons CTA redirigent vers : `https://19d7651f-4e24-4d23-ad4f-0ab1b902f33c.preview.emergentagent.com`

## 🎨 Design & Thème

- **Couleurs** : Dégradé bleu/violet (#3b82f6, #8b5cf6)
- **Thème** : Sombre avec effets glassmorphism
- **Typographie** : Segoe UI, moderne et lisible
- **Icônes** : Font Awesome 6
- **Animations** : CSS3 + JavaScript

## 📱 Fonctionnalités

### Site Web Marketing
- ✅ Présentation professionnelle
- ✅ Sections fonctionnalités détaillées  
- ✅ Statistiques impressionnantes
- ✅ Design responsive moderne
- ✅ SEO optimisé
- ✅ Animations fluides

### Application de Trading (Existante)
- ✅ Authentification utilisateur sécurisée
- ✅ Trading Forex (EUR/USD, XAU/USD)
- ✅ Levier illimité, spreads 0 pip
- ✅ Paiements Stripe LIVE (0% frais)
- ✅ Comptes demo/real séparés
- ✅ P&L temps réel, SL/TP automatiques

## 🚀 Instructions de Déploiement

### 1. Site Web (Netlify - Recommandé)
```bash
# Uploader le fichier /landing/index.html sur Netlify
# Ou connecter votre repo GitHub à Netlify
```

### 2. Application de Trading
```bash
# Backend (Railway/Heroku)
cd backend
# Configurer variables d'environnement :
# STRIPE_API_KEY=sk_live_...
# MONGO_URL=mongodb://...
# JWT_SECRET_KEY=...

# Frontend (Vercel/Netlify)  
cd frontend
# Configurer variables d'environnement :
# REACT_APP_BACKEND_URL=https://votre-backend.com
# REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### 3. Domaine Personnalisé
- **Site web** : `https://votre-domaine.com` 
- **Application** : `https://app.votre-domaine.com`

## 📞 Support & Contact

- **Email** : support@forexpro-trader.com
- **Téléphone** : +33 1 23 45 67 89
- **Adresse** : Paris, France

## ⚠️ Avertissements

Le trading sur le marché des changes (Forex) avec effet de levier présente des risques élevés et peut ne pas convenir à tous les investisseurs. Les performances passées ne garantissent pas les résultats futurs.

## 📄 Licence

© 2024 ForexPro Trader. Tous droits réservés.
