# coding: utf-8

#-------- Tokenization
def tokenize(code):
	import re
	ops = {
	  ';;;':  { 'code': 'push', 'arg': 'signed'},
	  ';;⁏':  { 'code': 'dup' },
	  ';⁏;':  { 'code': 'swap' },
	  ';⁏⁏':  { 'code': 'discard' },
	  '⁏;;':  { 'code': 'add' },
	  '⁏;⁏':  { 'code': 'sub' },
	  '⁏⁏;':  { 'code': 'mul' },
	  '⁏⁏⁏':  { 'code': 'div' },
	  '⁏  ':  { 'code': 'mod' },
	  '; ;':  { 'code': 'store' },
	  '; ⁏':  { 'code': 'retrieve' },
	  ' ;;':  { 'code': 'label', 'arg': 'unsigned' },
	  ' ;⁏':  { 'code': 'call', 'arg': 'unsigned' },
	  ' ; ':  { 'code': 'ret' },
	  ' ⁏ ':  { 'code': 'jump', 'arg': 'unsigned' },
	  ' ⁏;':  { 'code': 'jz', 'arg': 'unsigned' },
	  ' ⁏⁏':  { 'code': 'jn', 'arg': 'unsigned' },
	  '  ;':  { 'code': 'exit' },
	  '⁏ ;;': { 'code': 'outchar' },
	  '⁏ ;⁏': { 'code': 'outnum' },
	  '⁏ ⁏;': { 'code': 'readchar' },
	  '⁏ ⁏⁏': { 'code': 'readnum' },
	}
	
	make_int = lambda str:int(''.join('0' if c == ';' else '1' for c in str), 2)
	while code and code != '\n':
		has_match = False
		for key in ops:
			pattern = (key + (r'([;⁏]*)\n' if 'arg' in ops[key] else r'()') + r'(.*)$').decode('utf8')
			match = re.match(pattern, code, re.S)
			if match:
				has_match = True
				code = match.group(2)
				if 'arg' in ops[key]:
					if ops[key]['arg'] == 'unsigned':
						tokens.append([ops[key]['code'], 
									   make_int(match.group(1))])
					elif ops[key]['arg'] == 'signed':
						tokens.append([ops[key]['code'],
									   (1 if match.group(1)[0] == ';' else -1) * 
										make_int(match.group(1)[1:])])
				else:
					tokens.append([ops[key]['code']])
		if not has_match:
			raise Exception('Unknown command')

#-------- Interpretation
def jump(label):
	global pc
	for i in range(len(tokens)):
		if tokens[i][0] == 'label' and tokens[i][1] == label:
			pc = i
			break
	step()

def step():	
	global pc
	op = tokens[pc][0]
	arg = None if len(tokens[pc]) == 1 else tokens[pc][1]
	pc += 1
	if op == 'push':
		stack.append(arg)
		step()
	elif op == 'dup':
		stack.append(stack[-1])
		step()
	elif op == 'swap':
		stack[-1], stack[-2] = stack[-2], stack[-1]
		step()
	elif op == 'discard':
		stack.pop()
		step()
	elif op == 'add' or op == 'sub' or op == 'mul' or op == 'div' or op == 'mod':
		bin_ops = { 'add': '+', 'sub': '-', 'mul': '*', 'div': '/', 'mod': '%' }
		stack.append(eval(str(stack.pop()) + bin_ops[op] + str(stack.pop())))
		step()
	elif op == 'store':
		heap[stack[-2]] = stack[-1]
		stack.pop(); stack.pop()
		step()
	elif op == 'retrieve':
		stack.append(heap[stack.pop()])
		step()
	elif op == 'label':
		step()
	elif op == 'call':	
		call_stack.append(pc)
		jump(arg)
	elif op == 'ret':
		pc = call_stack.pop()
		step()
	elif op == 'jump':	
		jump(arg)
	elif op == 'jz':
		if stack.pop() == 0: jump(arg)
	elif op == 'jn':		
		if stack.pop() < 0: jump(arg)
	elif op == 'exit':
		sys.exit()
	elif op == 'outchar':
		print chr(stack.pop())
		step()
	elif op == 'outnum':
		print str(stack.pop())
		step()
	elif op == 'readchar':
		stack.append(ord(sys.stdin.read(1)))
		step()
	elif op == 'readnum':
		stack.append(int(sys.stdin.readline()))
		step()
	else:
		raise Exception('Unknown opcode')
		
#-------- Main
import sys
if len(sys.argv) == 2:
	tokens = []; pc = 0; heap = {}; stack = []; call_stack = []
	code = open(sys.argv[1], 'r').read().decode('utf8')
	tokenize(code)
	print tokens
	step()
else: print 'Usage: python semicolon.py [file.sc]'