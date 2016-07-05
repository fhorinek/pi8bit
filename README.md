# pi8bit - Hobby project
* logic simulator created to simulate 8-bit computer
* writtern in python using pygame (SDL)

## requirements
* python 2.7
* pygame
* pygtk (file dialog)

## app
* logic simulator is **opt/pybit.py**
 * you can load existing circuits or create new (using not existing filename)
* main file of the computer is **opt/inc/8_bit_computer.txt**
 * press RESET toggle in Clock control before doing anything!
* compiler is **opt/compiler/compile.py**
 * assembler command description **opt/compiler/asm_commands.txt**
 * binary instruction description **opt/compiler/instructions.txt**
 * standard output memory image with name **a.out** (you can load it by clicking on memory cell)

## controls
* left mouse - change state of inputs and tgl
* middle mouse - pan
* mouse weel - zoom
* Left ctrl - move mouse using the snap grid
* E - edit mode
  * A - add mode (right change cell, left place cell)
  * M - add module (right load cell, left place cell)
  * W - wiring (left place wire, right remove node or connection)
  * R - rename (rename cell, rename net, change label text)
  * Left shift - multipe selection
  * DEL - delete selected objects
  * ESC - return
* D - debug mode
  * space - stepping
  * ESC - return
