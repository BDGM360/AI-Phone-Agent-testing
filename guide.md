## Build an AI Phone Agent with Agora ConvoAI and SIP Gateway

![Derek](https://miro.medium.com/v2/resize:fill:64:64/1*YqlAbkszpPwYZVzcyZFAXA.jpeg)(https://medium.com/@derek_76692?source=post_page---byline--bca609a97775---------------------------------------)


In many industries, the phone remains the most trusted and natural way for users to seek help , calling about a technical issue, an appointment, or something far more personal. An interesting case that I learned last week in Manila is **tarot-based emotional counseling**. Many users prefer calling into a traditional hotline to receive private, empathetic advice from a tarot reader, especially when they feel vulnerable or simply want a more intimate experience.

That’s where this solution comes in: combining **SIP Gateway** infrastructure with **Agora** **ConvoAI**, a customizable conversational AI platform powered by LLMs and real-time voice features. Whether you’re building a **Tarot emotional counseling bot**, or a **24/7 support agent**, this architecture gives your users instant access to AI via a simple phone call — no apps, no downloads, no complexity.

## Use Cases: Solutions It Empowers

This architecture can be applied across many industries:

+   **Customer Support Hotlines**: Let AI handle FAQs and triage before escalation.
+   **Appointment Booking & Reminders**: Perfect for clinics, salons, and service providers.
+   **Emergency Service Operator**: Offer immediate attention before routing to the appropriate human responder.
+   **Retail Order Management**: Let customers call in to check order status, request returns, or modify delivery schedules.

## System Overview: How It Works

Here’s a high-level view of the workflow:

1.  **User Requests a PSTN Number**: You provision a PSTN number via SIP connection.
2.  **User Calls the Number**: The end-user dials in.
3.  **RTC Channel Connection**: Agora routes the call into an RTC channel.
4.  **Webhook Triggered**: When the user joins, a webhook is fired to your server.
5.  **Activate ConvoAI**: Your server starts the AI agent, which joins the channel and begins interacting with the caller.
6.  **Conversation Happens**: The user talks to the AI agent in real time.
7.  **User Hangs Up**: The leave event is captured via webhook.
8.  **Deactivate ConvoAI**: The AI agent is removed from the session.

## Step-by-Step: Integrating SIP Gateway and ConvoAI

## 1\. Activate a SIP Gateway service

Go to Agora support by emailing support@agora.io to register and receive an authentication header linked to your App ID.

## 2\. Obtain and Activate a PSTN Number

Make a POST request to Agora’s SIP service to provision a number, with the authentication header received in Step 1.

```
POST https://sipcm.agora.io/v1/api/pstn
```

Example JSON payload:

```
{
  "action": "inbound",
  "appid": "<<YOUR_APPID>>",
  "token": "<<TOKEN>>",
  "uid": "111",
  "channel": "<<CHANNEL_NAME>>",
  "region": "AREA_CODE_NA"
}
```

> ***Tip****: Use a fixed UID (e.g.,* `*111*`*) for PSTN users to simplify event handling logic.*

## 3\. Set Up Webhook Notifications

In the Agora Console, configure a webhook to receive event types `103` (join) and `104` (leave).

These events let your server know when to start or stop the AI agent.

## 4\. Implement Webhook Logic

Here’s a simplified version of the webhook logic in Python:

```
data.get('payload', {}).get('uid') == 111 and
data.get('productId') == 1
...if event_type == 103 and uid == 111:
    handle_convo_ai("start")  # Start AI when PSTN user joins
elif event_type == 104 and uid == 111:
    handle_convo_ai("stop")   # Stop AI when user hangs up
```

This connects ConvoAI to the RTC channel dynamically, so the agent is only active during a live call.

## 5\. Start/Stop ConvoAI via REST API

The backend communicates with ConvoAI using RESTful APIs following the guide [Agora Conversational AI Engine](https://docs.agora.io/en/conversational-ai/overview/product-overview?utm_source=medium&utm_medium=blog&utm_campaign=Build+an+AI-Powered+Phone+Support+Agent+Using+PSTN+and+ConvoAI).

+   Start the AI session
+   Join the RTC channel as an agent
+   Configure TTS, ASR, VAD, and LLM behavior
+   Terminate the session cleanly

## Example: Start Agent

```
url = f"{AGORA_AI_ENDPOINT}/projects/{APP_ID}/join"
payload = {
    "name": "pstnai",
    "properties": {
        "channel": CHANNEL_NAME,
        "token": generate_token(CHANNEL_NAME, "222"),
        "agent_rtc_uid": "222",
        "remote_rtc_uids": ["111"],
        ...
    }
}
```

## 6\. Customize Your AI Agent

ConvoAI allows deep customization:

+   **LLM Style**: Use OpenAI or other models
+   **Voice**: Integrated with ElevenLabs for natural TTS
+   **ASR**: Real-time speech recognition
+   **Agent Persona**: Script a friendly character with helpful behavior

> *The agent persona is defined via system prompts to provide warm, professional, and helpful responses, just like a real support agent.*
> 
> *Example: “You are Jack, a friendly and experienced Agora support agent…”*

## Try It Yourself

Once set up, users can simply dial the PSTN number and start talking to your AI agent instantly.

Demo Link: [https://ai-phone-agent-iota.vercel.app/](https://ai-phone-agent-iota.vercel.app/)

Git Repo: [https://github.com/AgoraIO-Solutions/AI-Phone-Agent](https://github.com/AgoraIO-Solutions/AI-Phone-Agent)

## Final Thoughts

This architecture isn’t just for support agent, it’s a gateway to deliver meaningful, conversational AI over the most widely used communication medium in the world: the telephone. Whether it’s a customer looking for help, or someone calling for emotional guidance through tarot, **SIP Gateway+ Agora ConvoAI** lets you serve them with intelligence, empathy, and scalability.

If you’re building **emotional wellness hotlines**, **tarot AI counselors**, or **personal guidance agents**, this is the infrastructure that can make it real — today.

**Additional Resources:**

Need direct consulting on AI voice solutions? Email me at derek@agora.io

Connect with me on LinkedIn — [Derek LinkedIn Profile](http://linkedin.com/in/derek-zheng-58611bb5)
