const OpenAI = require("openai");
require("dotenv").config();

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function moderateMessage(message) {
    console.log(message)
  try {
    const response = await openai.moderations.create({ input: message });
    return response.results[0].flagged;
  } catch (error) {
    console.error("Error with AI moderation:", error);
    return false; // If API fails, assume message is safe
  }
}

module.exports = { moderateMessage };
