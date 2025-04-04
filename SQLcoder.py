import os
from llama_cpp import Llama
import sys
import psycopg2
import json
from DebugLog import log_error

def sql_driver():
	cursor = None
	connect = None
	try:
		connect = psycopg2.connect(
			host='192.168.68.56',
			user='admin',
			password='admin123',
			port='5432',
			database='postgres'
		)
		connect.autocommit = True
		cursor = connect.cursor()

		sys.stderr = open(os.devnull, 'w')
		llm = Llama(model_path=os.path.join(os.path.dirname(__file__), './sqlcoder-7b-2.Q5_K_M.gguf'), use_mmap=False)

		with open(os.path.join(os.path.dirname(__file__), './Schema.json', 'r')) as f:
			schema = json.load(f)

		question = input('Type your SQL query: ')
		auto_correct = f'{schema} \nQuestion:\n {question}'

		output = llm(
			auto_correct,
			max_tokens=512,
			echo=False
		)
		output = output['choices'][0]['text']
		print(f'{output}\n')

		cursor.execute(output)
		rows = cursor.fetchall()
		for row in rows:
			print(row)

	except psycopg2.Error as e:
		print(f'Error in sql_driver: {e}')
		log_error(f'Error in sql_driver: {e}')

	finally:
		cursor.close()
		connect.close()