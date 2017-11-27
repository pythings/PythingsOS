for i in *.py; do
    [ -f "$i" ] || break
    echo "Porcessing $i"
    /home/xtensa/micropython-frozen/mpy-cross/mpy-cross $i
done
