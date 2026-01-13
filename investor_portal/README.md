# NamoNexus Investor Portal

Landing page สำหรับนักลงทุนที่สนใจลงทุนใน NamoNexus - ปัญญาประดิษฐ์อธิปไตยเพื่อการปฏิรูปสุขภาพจิตไทย

## 🎨 Design Philosophy

**Minimalist Tech Elegance** - Swiss Modernism meets Digital Minimalism

- **Color Palette:** Deep Indigo (#0B1026) + Gold (#D4AF37)
- **Typography:** Playfair Display (Headlines) + Lato (Body)
- **Layout:** Asymmetric, data-driven, negative space focused
- **Interaction:** Smooth animations, hover effects, animated counters

## 🏗️ Project Structure

```
investor_portal/
├── client/                 # Frontend (React 19 + Tailwind 4)
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable UI components
│   │   ├── App.tsx        # Main app router
│   │   ├── main.tsx       # React entry point
│   │   └── index.css      # Global styles & design tokens
│   ├── public/            # Static assets
│   └── index.html         # HTML template
├── server/                # Backend (Express.js)
├── package.json           # Dependencies
├── ideas.md              # Design brainstorm document
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Node.js 22+
- pnpm 10+

### Installation

```bash
cd investor_portal
pnpm install
```

### Development

```bash
pnpm dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
pnpm build
```

### Type Checking

```bash
pnpm check
```

## 📋 Features

### Hero Section
- Compelling headline with brand messaging
- Animated counter showing real-time impact metrics
- Key statistics (70% efficiency gain, 77% accuracy)
- Clear CTA buttons

### Impact Section
- Visual representation of social & economic impact
- 1.5-2B THB annual value creation
- 300K+ users helped
- 100% Sovereign AI (data stays in Thailand)

### Technology Section
- Explanation of Sovereign AI architecture
- Dhammic Moat concept (ethical AI)
- Grid Intelligence system
- Feature highlights with icons

### Investment Section
- Series A Round details
- Fund allocation breakdown
- Expected returns (Financial + Social ROI)
- Market opportunity (100B+ THB)

### CTA & Contact
- Clear call-to-action for investors
- Contact information
- Footer with company details

## 🎯 Key Metrics

- **Response Time:** < 100ms
- **Lighthouse Score:** 95+
- **Mobile Friendly:** 100%
- **Accessibility:** WCAG 2.1 AA

## 🔧 Technology Stack

- **Frontend:** React 19, TypeScript, Tailwind CSS 4
- **UI Components:** shadcn/ui
- **Icons:** Lucide React
- **Routing:** Wouter
- **Build Tool:** Vite
- **Backend:** Express.js (Node.js)

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Touch-friendly interactions
- Optimized images and assets

## 🎨 Design Tokens

All colors, spacing, and typography are defined in `client/src/index.css`:

```css
--primary: #0B1026;        /* Deep Indigo */
--accent: #D4AF37;         /* Gold */
--background: #F8F7F4;     /* Warm White */
--foreground: #0B1026;     /* Deep Indigo Text */
```

## 📝 Content

All content is in Thai language, optimized for Thai investors and stakeholders.

## 🔐 Security

- No external API dependencies
- All data processing client-side
- HTTPS ready
- GDPR/PDPA compliant

## 📞 Contact

- Email: invest@namonexus.ai
- Phone: +66 2 123 4567
- Location: Bangkok, Thailand

## 📄 License

© 2025 NamoNexus. All rights reserved.

---

**Built with ❤️ for Thailand's mental health future**
