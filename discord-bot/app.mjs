import dotenv from 'dotenv';
import { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder } from 'discord.js';
import OpenAI from 'openai';

// Load environment variables from .env file
dotenv.config();

// Validate required environment variables
const required = ['DISCORD_TOKEN', 'APPLICATION_ID', 'GUILD_ID', 'OPENAI_API_KEY'];
for (const name of required) {
  if (!process.env[name]) {
    console.error(`Missing required environment variable: ${name}`);
    process.exit(1);
  }
}

const { DISCORD_TOKEN, APPLICATION_ID, GUILD_ID, OPENAI_API_KEY } = process.env;

// Initialize OpenAI client
const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

// Define the /ask slash command
const commands = [
  new SlashCommandBuilder()
    .setName('ask')
    .setDescription('Ask a question to ChatGPT')
    .addStringOption(option =>
      option
        .setName('prompt')
        .setDescription('Your question')
        .setRequired(false)
    )
    .toJSON()
];

// Register slash commands for the guild
async function registerCommands() {
  const rest = new REST({ version: '10' }).setToken(DISCORD_TOKEN);
  try {
    console.log('Registering slash commands...');
    await rest.put(
      Routes.applicationGuildCommands(APPLICATION_ID, GUILD_ID),
      { body: commands }
    );
    console.log('Slash commands registered.');
  } catch (err) {
    console.error('Failed to register slash commands:', err);
  }
}

// Send a prompt to OpenAI and return the response string
async function fetchOpenAIResponse(prompt) {
  const completion = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [{ role: 'user', content: prompt }]
  });
  return completion.choices?.[0]?.message?.content?.trim();
}

// Create Discord client
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

client.once('ready', () => {
  console.log(`Logged in as ${client.user.tag}`);
});

// Handle slash command interactions
client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand() || interaction.commandName !== 'ask') return;

  const prompt = interaction.options.getString('prompt');

  if (!prompt) {
await interaction.reply({
      content:
        'Hello! I am here to help with any questions you may have. How can I assist you today?',
      ephemeral: true
    });
    return;
  }

  try {
    return;
  }

  try {
    await interaction.deferReply();
    const response = await fetchOpenAIResponse(prompt);
    await interaction.editReply(response ?? 'No response from OpenAI.');
  } catch (err) {
    console.error('OpenAI error:', err);
    await interaction.editReply('Failed to fetch a reply from OpenAI.');
  }
});

// Handle messages starting with !ask
client.on('messageCreate', async message => {
  if (message.author.bot) return;

  const prefix = '!ask ';
  if (!message.content.toLowerCase().startsWith(prefix)) return;

  const prompt = message.content.slice(prefix.length).trim();
  if (!prompt) return;

  try {
    const response = await fetchOpenAIResponse(prompt);
    await message.reply(response ?? 'No response from OpenAI.');
  } catch (err) {
    console.error('OpenAI error:', err);
    await message.reply('Failed to fetch a reply from OpenAI.');
  }
});

// Start the bot
(async () => {
  await registerCommands();
  try {
    await client.login(DISCORD_TOKEN);
  } catch (err) {
    console.error('Discord login failed:', err);
  }
})();
