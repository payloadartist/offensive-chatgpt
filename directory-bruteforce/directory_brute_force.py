"""
Usage: python3 directory_brute_force.py https://example.org directory_list.txt
Credits: ChatGPT
"""
import argparse
import concurrent.futures
import os
import re
import signal
import sys
import time
import requests


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Directory brute-force tool"
    )
    parser.add_argument(
        "url",
        help="The URL to brute-force."
    )
    parser.add_argument(
        "wordlist",
        help="The path to the wordlist file."
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=5,
        help="The number of threads to use."
    )
    parser.add_argument(
        "-m", "--match",
        help="The text to match in the response."
    )
    return parser.parse_args()


def signal_handler(signal, frame):
    print("\n")
    response = input("Do you want to quit? [y/N] ")
    if response.lower() in ["y", "yes"]:
        print("Exiting...")
        sys.exit(0)


def check_url(url, directory):
    full_url = f"{url}/{directory}"
    try:
        response = requests.get(full_url)
    except requests.RequestException:
        return None
    else:
        if args.match:
            if re.search(args.match, response.text):
                return full_url
        else:
            if response.status_code == 200:
                return full_url
        return None


def main():
    global args
    args = parse_arguments()
    signal.signal(signal.SIGINT, signal_handler)

    with open(args.wordlist) as wordlist_file:
        directories = [line.strip() for line in wordlist_file]

    results = []
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_directory = {
            executor.submit(check_url, args.url, directory): directory
            for directory in directories
        }
        for future in concurrent.futures.as_completed(future_to_directory):
            directory = future_to_directory[future]
            try:
                result = future.result()
            except Exception:
                pass
            else:
                if result:
                    results.append(result)
            finally:
                directories.remove(directory)
                print(f"{len(directories)} directories left to check", end="\r")

    elapsed_time = time.time() - start_time
    print(f"\n{len(results)} directories found in {elapsed_time:.2f} seconds")
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
    
