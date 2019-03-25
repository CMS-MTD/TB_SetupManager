Repo for the code that manage the TB setup running on the Raspberry Pi (for the moment).

# Operations

## Run the program
```
make; ./OTSDAQInterface &> log.log &
```

## Control commands
Set the X position to <kk> mm:
```
echo <kk> > MotionStage/x_stage/user_set_position.txt
```
