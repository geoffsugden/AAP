import asyncio
import sys
import credentials

host = credentials.host 
port = credentials.port 

async def listen_to_socket(reader):
    """Continuously listen to messages from the socket."""
    try:
        while True:
            data = await reader.read(512)
            if not data:
                print("\nConnection closed by server.")
                break
            msg = data.decode('utf-8')
            print(trans_code(msg))
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"\n[ERROR] Listening failed: {e}")


async def read_user_input(writer):
    """Read user input and send messages to the socket."""
    loop = asyncio.get_event_loop()
    try:
        while True:
            user_input = await loop.run_in_executor(None, sys.stdin.readline)
            if user_input.strip().lower() == "exit":
                print("Exiting...")
                break
            msg = trans_code(user_input)
            writer.write(msg.encode('utf-8'))
            await writer.drain()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[ERROR] Sending failed: {e}")


async def main():
    try:
        reader, writer = await asyncio.open_connection(host, port)

        # Start listening and input tasks
        listen_task = asyncio.create_task(listen_to_socket(reader))
        input_task = asyncio.create_task(read_user_input(writer))

        # Wait for input to finish (user typed 'exit')
        await input_task

        # Cancel listener and close connection
        listen_task.cancel()
        await listen_task

        writer.close()
        await writer.wait_closed()
    except ConnectionRefusedError:
        print(f"Unable to connect to {host}:{port}")
    except Exception as e:
        print(f"[ERROR] {e}")

def trans_code(code):
    trans_dict = {
        'ZO1': 'Garage Door Open',
        'ZC1': 'Garage Door Closed',
        'ZO2': 'Movement Detected in Garage',
        'ZC2': '',
        'ZO3': 'Movement Detected in Lounge',
        'ZC3': '',
        'ZO4': 'Movement Detected in Guest Bedroom',
        'ZC4': '',
        'ZO5': 'Movement Detected in Office',
        'ZC5': '',
        'ZO6': 'Movement Detected in Master Bedroom',
        'ZC6': '',
        'ZO7': 'Master Bedroom Door Open',
        'ZC7': 'Master Bedroom Door Closed',
        'NR': 'System not ready',
        'RO': 'System ready',
        'OG': 'OUTPUTON 4\n'
    }
    if code.strip() in trans_dict:
        return trans_dict[code.strip()]
    else: 
        return code

if __name__ == "__main__":
    asyncio.run(main())
