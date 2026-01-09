# 🎮 Abitus RPG

> *Level up your real life through epic quests and meaningful progression*

Abitus is a cross-platform gamified self-improvement application that transforms personal growth into an engaging role-playing experience. Built with [Flet](https://flet.dev/), it runs natively on iOS, Android, Windows, Linux, macOS, and web browsers.

## ✨ Concept

Life improvement doesn't have to feel like a chore. Abitus reimagines personal development as an RPG adventure where:

- **You are the hero** of your own story
- **Life dimensions become character stats** that you actively level up
- **Goals transform into quests** with clear objectives and rewards
- **Progress is visible and rewarding** through XP, achievements, and unlockables

## 🎯 Core Features

### Character Assessment
When you begin your journey, Abitus conducts an immersive assessment through thoughtful questions to understand:
- Your current status across all life dimensions
- Your aspirations and desired future state
- Your available time and energy capacity
- Your preferred challenge level

### Life Dimensions (Stats)

Your character sheet tracks six core attributes:

| Stat | Icon | Description |
|------|------|-------------|
| **Intellect** | 📚 | Knowledge, learning, creativity, problem-solving |
| **Vitality** | 💪 | Physical health, fitness, energy, nutrition |
| **Spirit** | 🧘 | Emotional wellbeing, mindfulness, resilience |
| **Bonds** | 💝 | Relationships, social connections, communication |
| **Prosperity** | 💰 | Career, finances, professional growth |
| **Mastery** | 🎯 | Skills, hobbies, personal projects |

### Quest System

Quests are generated based on the gap between your current stats and desired state. They come in various forms:

**Quest Types:**
- 🗡️ **Daily Quests** — Small, repeatable tasks (5-15 min)
- 🛡️ **Weekly Challenges** — Medium commitments with greater rewards
- 🏰 **Epic Quests** — Multi-week pursuits for major stat boosts
- 🎲 **Random Encounters** — Surprise opportunities for bonus XP
- 👥 **Party Quests** — Collaborative goals involving others

**Quest Examples:**
- *"The Scholar's Path"* — Read for 20 minutes (Intellect +10 XP)
- *"Iron Body Initiation"* — Complete a 15-minute workout (Vitality +15 XP)
- *"The Gratitude Scroll"* — Write 3 things you're grateful for (Spirit +10 XP)
- *"The Social Guild"* — Reach out to a friend you haven't spoken to (Bonds +20 XP)
- *"The Artisan's Trial"* — Spend 30 minutes on a creative hobby (Mastery +15 XP)

### Progression System

- **Experience Points (XP)** — Earned by completing quests
- **Levels** — Each stat levels up independently as you gain XP
- **Achievements** — Unlock badges for milestones and streaks
- **Titles** — Earn character titles based on your strongest stats
- **Skill Trees** — Unlock specialized quests as you progress

### Adaptive Difficulty

The quest generator considers:
- Your current capacity and energy levels
- Past quest completion rates
- Time since last activity in each dimension
- Seasonal and contextual factors

## 🛠️ Technical Stack

- **Framework:** [Flet](https://flet.dev/) — Cross-platform Python UI framework
- **Language:** Python 3.10+
- **UI Rendering:** Flutter (via Flet)
- **Data Storage:** Local SQLite with optional cloud sync
- **Platforms:** iOS, Android, Windows, macOS, Linux, Web

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/abitus.git
cd abitus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
flet run main.py
```

## 🚀 Running on Different Platforms

```bash
# Desktop (native window)
flet run main.py

# Web browser
flet run main.py --web

# iOS/Android (requires Flet app installed on device)
flet run main.py --ios
flet run main.py --android
```

## 📁 Project Structure

```
abitus/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md
├── assets/                 # Images, icons, sounds
│   ├── icons/
│   └── images/
├── src/
│   ├── models/            # Data models
│   │   ├── character.py   # Player character & stats
│   │   ├── quest.py       # Quest definitions
│   │   └── achievement.py # Achievement system
│   ├── views/             # UI screens
│   │   ├── home.py        # Main dashboard
│   │   ├── character.py   # Character sheet
│   │   ├── quests.py      # Quest log
│   │   ├── assessment.py  # Initial assessment
│   │   └── settings.py    # App settings
│   ├── services/          # Business logic
│   │   ├── quest_generator.py
│   │   ├── progression.py
│   │   └── storage.py
│   └── components/        # Reusable UI components
│       ├── stat_bar.py
│       ├── quest_card.py
│       └── achievement_badge.py
└── data/
    └── quest_templates.json
```

## 🎨 Design Philosophy

Abitus embraces these principles:

1. **Intrinsic Motivation** — Quests are designed to be inherently rewarding, not just check-boxes
2. **Sustainable Progress** — Small, consistent actions beat burnout-inducing sprints
3. **Holistic Growth** — Balance across dimensions prevents neglecting important life areas
4. **Personal Agency** — You choose which quests to accept; the game adapts to you
5. **Celebration** — Every win, no matter how small, deserves recognition

## 🗺️ Roadmap

- [x] Core character assessment flow
- [x] Basic quest system with daily quests
- [x] Stat tracking and visualization
- [x] Achievement system
- [x] Interview-style character assessment (natural questions instead of sliders)
- [x] Multi-faceted dimensions (sub-scores that aggregate into main stats)
- [-] Weekly and epic quest chains
- [ ] Cloud sync and backup
- [ ] Social features (party quests, leaderboards)
- [ ] Custom quest creation
- [ ] AI-powered quest suggestions
- [ ] Habit streak tracking
- [ ] Integration with health apps
- [ ] Journal feature integrated with quests (e.g. gratitude entries, reflections)
- [ ] App integrations via Zapier or direct APIs (Duolingo, fitness apps, etc.) for auto-completing quests

## 🤝 Contributing

Contributions are welcome! Whether it's new quest ideas, UI improvements, or bug fixes, feel free to open an issue or submit a pull request.

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

---

*"The journey of a thousand miles begins with a single quest."* 🌟

