import os
from llama_cpp import Llama
import sys
import psycopg2
import json
from DebugLog import log_error
from Connection import connect

def sql_driver():
	conn = None
	cursor = None
	try:
		conn = connect()
		connect.autocommit = True
		cursor = conn.cursor()

		sys.stderr = open(os.devnull, 'w')
		llm = Llama(model_path=os.path.join(os.path.dirname(__file__), './sqlcoder-7b-2.Q5_K_M.gguf'), use_mmap=False)

		with open(os.path.join(os.path.dirname(__file__), 'Schema.json')) as f:
			schema = json.load(f)

		prompt = (
			'ONLY return a pure SQL query that can be executed directly in PostgreSQL. '
			'Do NOT explain, comment, or include anything else except the SQL query.\n'
		)

		question = input('Type your SQL query: ')
		auto_correct = f'{prompt} \n{schema} \nQuestion:\n {question}'

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
		conn.close()