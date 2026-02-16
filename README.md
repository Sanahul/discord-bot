# discord-bot

A Discord bot with a comprehensive middleman ticket system for facilitating trades.

## Features

### Middleman Ticket System
- **Modal-based ticket creation** with 3 questions
- **Automatic private channel creation** for each ticket
- **Role-based access control** for staff
- **Button interface** for easy ticket management
- **Ticket tracking and logging**
- **Multiple ticket management commands**

See [TICKET_SYSTEM.md](TICKET_SYSTEM.md) for detailed documentation.

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Discord bot token as an environment variable:
   ```bash
   export DISCORD_TOKEN="your-token-here"
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

### Bot Commands
- `$purge <amount>` - Delete messages (requires Manage Messages permission)
- `$serverinfo` - Display information about the server
- `$mminfo` - Display information about how the Middleman system works
- `$fee` - Display middleman fee information with payment options
- `$confirm @user1 @user2` - Create a trade confirmation request with buttons (restricted to the two mentioned users)

### Ticket System Commands

**User Commands:**
- `$add @user` - Add a person to the ticket
- `$remove @user` - Remove a person from the ticket
- `$renameticket {name}` - Rename the ticket

**Staff Commands (Middleman Role Required):**
- `$claim` - Claim the ticket
- `$unclaim` - Unclaim the ticket
- `$transfer @user` - Transfer ticket to another middleman
- `$close` - Close the current ticket

**Admin Commands:**
- `$ticketpanel` - Create the ticket panel
- `$setsupportrole @role` - Set the support/middleman role
- `$setticketcategory CategoryName` - Set ticket category
- `$setlogchannel #channel` - Set log channel

## Setup

1. Create a "Middleman" or "Support" role in your Discord server (or use the `$setsupportrole` command)
2. Run `$ticketpanel` in the channel where you want users to create tickets
3. Users can click the "Create Ticket" button to start

## License

MIT