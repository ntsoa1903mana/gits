import asyncio
import sys
import time
from pathlib import Path

import g4f  # Assuming 'g4f' is a valid library
from fastapi import FastAPI, HTTPException

sys.path.append(str(Path(__file__).parent.parent))

app = FastAPI()

# Define a list of providers to choose from
PROVIDERS = [
    g4f.Provider.AItianhu,
    g4f.Provider.Acytoo,
    g4f.Provider.Aichat,
    g4f.Provider.Ails,
    g4f.Provider.Aivvm,
    g4f.Provider.ChatBase,
    g4f.Provider.ChatgptAi,
    g4f.Provider.ChatgptLogin,
    g4f.Provider.CodeLinkAva,
    g4f.Provider.DeepAi,
    g4f.Provider.Opchatgpts,
    g4f.Provider.Vercel,
    g4f.Provider.Vitalentum,
    g4f.Provider.Wewordle,
    g4f.Provider.Ylokh,
    g4f.Provider.You,
    g4f.Provider.Yqcloud,
]

# Define the default provider and GPT-3.5 Turbo model
DEFAULT_PROVIDER = g4f.Provider.Wewordle
GPT_MODEL = None

# Initialize the current provider with the default provider
GPT_PROVIDER = DEFAULT_PROVIDER

# Initialize the last known healthy provider with the default provider
LAST_KNOWN_HEALTHY_PROVIDER = DEFAULT_PROVIDER


async def check_provider_health(provider):
    try:
        response = await provider.create_async(
            model=None,
            messages=[
                {"role": "system", "content": " "},
                {"role": "user", "content": "HI"}
            ]
        )
        print(f"{provider.__name__}:")
        #print("Response:", response)
        #print()

        # Check if "hello" is in the response content and return the result
        return "hello" in str(response).lower()
    except Exception as e:
        print(f"Error testing {provider.__name__}: {str(e)}")
        #print()
        return False


async def update_provider_on_error():
    global GPT_PROVIDER, LAST_KNOWN_HEALTHY_PROVIDER
    for provider in PROVIDERS:
        if await check_provider_health(provider):
            GPT_PROVIDER = provider
            LAST_KNOWN_HEALTHY_PROVIDER = (
                provider  # Update the last known healthy provider
            )
            print(f"Provider switched to: {provider}")
            return


@app.get("/")
async def home():
    print("Home endpoint reached")
    return {"message": "OK"}


@app.post("/generate-response")
async def generate_response(data: dict):
    model=model = g4f.models.gpt_35_turbo.name if GPT_PROVIDER.supports_gpt_35_turbo else g4f.models.default.name
    try:
        fbid = data.get("fbid", "")  # Get the 'fbid' from the request data
        user_message = data.get("prompt", "")
        #stream = False
        messages = [
            {
                "role": "system",
                "content": " ",
            },
            {"role": "user", "content": user_message},
        ]

        async def generate_response_async():
            start_time = time.time()

            response = await GPT_PROVIDER.create_async(
                model=model,
                messages=messages,
                #stream=stream,
                #active_server=30,
            )

            end_time = time.time()
            elapsed_time = end_time - start_time

           # print(response)
            print(GPT_PROVIDER)
            print(f"Response generated in {elapsed_time:.2f} seconds")

            # Return the response with 'fbid'
            return {"fbid": fbid, "response": response}

        # Execute the asynchronous response generation function concurrently
        response = await asyncio.gather(generate_response_async())
        return response[0]
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Handle the error by triggering the provider update

        await update_provider_on_error()
        print("Provider switched due to error")
        new_exception = HTTPException(status_code=500, detail="Error gen response")
        new_exception.__cause__ = e  # Attach the original exception as the cause
        raise new_exception


if __name__ == "__main__":
    import uvicorn

    print("Starting UVicorn server")
    uvicorn.run(app, host="0.0.0.0", port=5000)
