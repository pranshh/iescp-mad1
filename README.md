# Influencer Engagement and Sponsorship Coordination Platform

This platform connects **Sponsors** and **Influencers** to collaborate on advertising campaigns. Sponsors can promote their products or services, while Influencers can monetize their social media presence by accepting ad requests. The platform facilitates campaign management, ad request negotiations, and user engagement.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Roles](#roles)
  - [Admin](#admin)
  - [Sponsor](#sponsor)
  - [Influencer](#influencer)
- [Core Functionalities](#core-functionalities)
  - [Admin](#admin)
  - [Sponsors](#sponsors)
  - [Influencers](#influencers)
- [Installation](#installation)

---

## Features
- Role-based access: Admin, Sponsor, Influencer
- Campaign creation and management for sponsors
- Influencers can accept, reject, or negotiate ad requests
- Admin dashboard for monitoring users, campaigns, and flagged content
- Search functionalities for sponsors (to find influencers) and influencers (to find public campaigns)

---

## Technologies Used
- **Flask**: Backend framework
- **Jinja2**: Template rendering
- **Bootstrap**: Frontend styling
- **SQLite**: Database for persistent data storage

---

## Roles

### Admin
- Full access to the platform
- Can monitor all users, campaigns, and ad requests
- Can flag inappropriate campaigns or users

### Sponsor
- Creates campaigns to advertise products/services
- Can send ad requests to influencers
- Manages campaign budgets and timelines
- Can view and search for relevant influencers based on reach and niche

### Influencer
- Receives ad requests from sponsors
- Can accept or reject ad requests and negotiate terms
- Can search for public campaigns based on category and budget
- Can update their profile page (publicly visible)

---

## Core Functionalities

### Admin
- **Dashboard**: View statistics on active users, campaigns (public/private), ad requests, and flagged sponsors/influencers
- **Flag Management**: Ability to flag inappropriate users or campaigns

### Sponsors
- **Campaign Management**: Create, update, and delete campaigns, setting visibility as public or private
- **Ad Requests**: Create, edit, and delete ad requests. Manage interactions with influencers
- **Search Influencers**: Find influencers by niche, reach, or followers

### Influencers
- **Ad Request Management**: View ad requests, accept/reject them, or negotiate payment terms
- **Search Campaigns**: Find relevant public campaigns based on niche and budget
- **Profile Management**: Update public profile with information like name, category, niche, and reach

---

## Installation

To set up the project locally:

1. Clone the repository:
   ```
   git clone https://github.com/pranshh/iescp-mad1.git
   ```

2. Navigate to the project directory:
   ```
   cd iescp-mad1
   ```

3. Create and activate a virtual environment:
   ```
   python -m venv myenv
   myvenv\Scripts\activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the project:
   ```
   python app.py
   ```
---