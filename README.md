#Off
A text-based rpg for the messaging client Slack.
##Getting Started
First, install Python 3.6.x on to your computer.

Next you will need to import the following:
<pre><code>pip install python-firebase
pip install slackclient
pip install requests</code></pre>

To get the BOT_ID for your Slack Bot you will need to run the following file. Before you run this code, change the Slack Token in line 7 to a slack token you need to create. You can easily create a slack token using: https://api.slack.com/docs/oauth-test-tokens
<pre><code>python print_bot_id.py</code></pre>

Using the BOT_ID you found using the previous command and the Slack Token you created, set up your bot in your repository.
<pre><code>export BOT_ID='U4AA1UYN7'
export SLACK_BOT_TOKEN='xoxb-146341984755-1fYi3Oau3Cx262xcxP3Tzzp0'
</code></pre>

##List of Commands
<ul>
<li>adventure:<code>@Bot adventure</code>
  If your character is in stages 0, 1, and 2. This allows your character to progress to the next stage.
</li>
<li>allocate:<code>@Bot allocate attribute numPoints</code>
  This will allocate the specified number of allocation points to the attribute.
</li>
<li>attack:<code>@Bot attack</code>
  If your character is in an encounter with an enemy, this command will allow you to start attacking. In each attack, both the character and the enemy will attack in an order decided on by luck.
</li>
<li>buy:<code>@Bot buy item</code>
  Use buy to purchase items from the general manager in the village.
</li>
<li>drink:<code>@Bot drink item</code>
  Use this command to drink potions to increase your character's health.
</li>
<li>equip:<code>@Bot equip armor</code>
Changes your current armor to another specified armor in your inventory.
</li>
<li>exp:<code>@Bot exp</code>
  Allows you to see your experience points and allocation points.
</li>
<li>flee:<code>@Bot flee</code>
  If your character has encountered an enemy, this command will allow you to flee back to the village. By doing this, you will be reset back to stage 0 or your current adventure.
</li>
<li>help:<code>@Bot help</code>
  This command will print a list of all commands you can use in the game.
</li>
<li>inventory:<code>@Bot inventory</code>
  Allows you to see all the items in your invetory.
</li>
<li>money:<code>@Bot money</code>
  This will return the amount of money you currently have in your inventory.
</li>
<li>newChar:<code>@Bot newChar characterName</code>
  Creates a new character for your username. Each Slack user can have multiple characters, each is stored in firebase with it's information.
</li>
<li>sell:<code>@Bot sell item</code>
  This allows you to sell an item from your inventory to the general manager in the village.
</li>
<li>stats:<code>@Bot stats</code>
  Will display your character's attributes.
</li>
<li>tradelist:<code>@Bot tradelist</code>
  This will shows the items the general manager has to sell in the town.
</li>
<li>wield:<code>@Bot wield weapon</code>
  Changes your current weapon to another specified weapon in your inventory.
</li>
<li>whereami:<code>@Bot whereami</code>
  Tells you which village you had previously visited. This also specifies the pack of enemies in this area.
</li>
</ul>
