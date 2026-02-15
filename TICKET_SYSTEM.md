# Middleman Ticket System

A comprehensive ticket system for Discord bot to facilitate middleman trading.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure the Bot

The bot will automatically detect roles named "Middleman" or "Support". Alternatively, use admin commands to configure:

```
$setsupportrole @RoleName   - Set the middleman/support role
$setticketcategory CategoryName - Set category for ticket channels
$setlogchannel #channel-name - Set channel for ticket logs
```

### 3. Create Ticket Panel

Use the admin command to create a ticket panel:
```
$ticketpanel
```

This will create an embed with a "Create Ticket" button that users can click.

## Features

### Ticket Creation
- Users click the "Create Ticket" button
- Fill out a modal form with 3 questions:
  1. What is the other trader user?
  2. What are you giving?
  3. What is the other trader giving?
- Automatically creates a private ticket channel
- Pings support team and ticket creator

### Ticket Management Commands

All commands work within ticket channels:

**User Commands:**
- `$add @user` - Add a person to the ticket
- `$remove @user` - Remove a person from the ticket
- `$renameticket {name}` - Rename the ticket

**Staff Commands (Middleman Role Required):**
- `$claim` - Claim the ticket
- `$unclaim` - Unclaim the ticket
- `$transfer @user` - Transfer ticket to another middleman
- `$close` - Close the current ticket

### Button System

**Create Ticket Button** - Users click to create new tickets
**Claim Button** - Staff can claim tickets
**Close Button** - Staff can close tickets

## Permissions

### Required Bot Permissions:
- Manage Channels
- Manage Messages
- Read Messages
- Send Messages
- Embed Links
- Attach Files
- Manage Roles (for channel permissions)

### Staff Role:
By default, the bot looks for roles containing "middleman" or "support" in their name. You can also set a specific role using `$setsupportrole`.

Staff members can:
- Claim tickets
- Unclaim tickets
- Transfer tickets
- Close tickets

### Regular Users:
Can:
- Create tickets
- Add/remove users from their tickets
- Rename their tickets

## Configuration

### Admin Commands:
- `$ticketpanel` - Create the ticket panel
- `$setsupportrole @role` - Set the support/middleman role
- `$setticketcategory CategoryName` - Set ticket category
- `$setlogchannel #channel` - Set log channel

## Ticket Workflow

1. **User creates ticket** → Private channel created
2. **Staff claims ticket** → Ticket status updated
3. **Trade facilitation** → Staff helps with the trade
4. **Staff closes ticket** → Channel deleted after 5 seconds

## Data Tracking

Each ticket stores:
- Ticket number
- Creator
- Other trader information
- What each party is giving
- Claimed by (if claimed)
- Status (open, claimed, closed)
- Creation timestamp
- Renamed status

## Security Features

- Private channels (only creator and staff can see)
- Role-based access control
- Permission checks on all commands
- Automatic logging of ticket actions
- Cannot remove ticket creator from channel

## Notes

- Ticket channels are automatically deleted 5 seconds after closing
- Renamed tickets won't auto-close after 1 hour
- All ticket actions are logged to the configured log channel
- Buttons are persistent (work after bot restart)
