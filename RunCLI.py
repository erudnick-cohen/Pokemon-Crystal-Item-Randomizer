import os
import sys

from RunGUI import ItemRandomiser


def runCLI(arguments):
	arg_error = False

	if "input" not in arguments:
		print("No --input or -i provided.", file=sys.stderr)
		arg_error = True

	if "output" not in arguments:
		print("No --output or -o provided.", file=sys.stderr)
		arg_error = True

	if "mode" not in arguments:
		print("No --mode or -m provided.", file=sys.stderr)
		arg_error = True

	if "race" in arguments and "log" in arguments:
		print("Cannot use race mode and spoiler log.", file=sys.stderr)
		arg_error = True

	use_seed = None
	if "seed" in arguments:
		use_seed = arguments["seed"]

	if "race" in arguments :
		if type(arguments["race"]) is not bool:
			race_mode = arguments["race"]
		else:
			race_mode = None
	else:
		race_mode = None

	if arg_error:
		return

	#app = QApplication(sys.argv)
	#form = RunWindow()

	# Need to load settings, etc.

	item_rando = ItemRandomiser(GUI=None)

	if race_mode is None:
		settingsFile = arguments["mode"]
		item_rando.loadSettings(settingsFile)
		rom_md5 = None
	else:
		data = item_rando.LoadRaceModeSettings(raceString=race_mode)
		use_seed = data[2]
		rom_md5 = data[3]


	flags = {"Spoiler" : "log" in arguments, "RaceMode": "race" in arguments}
	print(flags, arguments)

	item_rando.runRandomizer(in_file=arguments["input"], out_file=arguments["output"],
							 seed=use_seed, run_flags=flags, requiredMD5=rom_md5)


	#form.romPath = arguments["input"]
	#form.runRandomizer(cli=True, outputFile=arguments["output"])

	if arg_error:
		return

def convertArgument(argument):
	if argument == "i":
		return "input"

	if argument == "o":
		return "output"

	if argument == "m":
		return "mode"

	if argument == "s":
		return "seed"

	if argument == "l":
		return "log"

	if argument == "r":
		return "race"

	return argument

def parseArguments():
	parsed_args = {}
	read_next_arg = 0
	for argument in sys.argv:

		if os.getcwd() in argument:
			continue

		if read_next_arg > 0 and argument.startswith("-"):
			arg_name = convertArgument(arg_name)
			parsed_args[arg_name] = True

		if argument.startswith("--"):
			arg_name = argument[2:]
			read_next_arg = 2
			pass
		elif argument.startswith("-"):
			arg_name = argument[1:]
			read_next_arg = 1
			pass
		elif read_next_arg > 0:
			if read_next_arg == 1:
				arg_name = convertArgument(arg_name)

			parsed_args[arg_name] = argument

			read_next_arg = 0
		else:
			parsed_args[argument] = True

	if read_next_arg == 2:
		parsed_args[arg_name] = True
	elif read_next_arg == 1:
		parsed_args [convertArgument(arg_name)] = True

	return parsed_args


def main():
	arguments = parseArguments()
	if "cli" in arguments:
		runCLI(arguments)
		return
	else:
		print("cli argument must be provided.")


if __name__ == '__main__':
	main()