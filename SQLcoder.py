import os
from llama_cpp import Llama
import sys
import psycopg2
import json
from DebugLog import log_error
from Connection import connect, cuda_available, estimate_n_gpu_layers

def sql_driver():
	conn = None
	cursor = None
	try:
		conn = connect()
		connect.autocommit = True
		cursor = conn.cursor()

		sys.stderr = open(os.devnull, 'w')

		vram_gb = cuda_available()
		if vram_gb > 0:
			n_gpu_layers = estimate_n_gpu_layers(vram_gb)

		else:
			n_gpu_layers = 0

		llm = Llama(model_path=os.path.join(os.path.dirname(__file__), './sqlcoder-7b-2.Q5_K_M.gguf'), use_mmap=False, n_gpu_layers=n_gpu_layers)

		with open(os.path.join(os.path.dirname(__file__), 'Schema.json')) as f:
			schema = json.load(f)

		prompt = (
			"ONLY return a pure SQL query that can be executed directly in PostgreSQL. "
			"Do NOT explain, comment, or include anything else except the SQL query. "
			"Use ILIKE or LOWER(...) for text comparisons to make them case-insensitive.\n\n"
			"Available tables and their columns:\n"
		)

		for table in schema:
			table_name = table["table"]
			prompt += f"\nTable '{table_name}' has the following columns:\n"
			for col in table["columns"]:
				col_name = col["name"]
				description = ""
				if col_name == "part_name":
					description = " – name of the part, like 'Spark Plug' or 'Air Filter'"
				elif col_name == "part_number":
					description = " – unique identifier code for the part"
				elif col_name == "category":
					description = " – part category, like 'engine', 'brakes', etc."
				elif col_name == "price":
					description = " – price of the part in euros"
				elif col_name == "id":
					description = " – unique serial identifier"
				prompt += f" - {col_name}{description}\n"

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