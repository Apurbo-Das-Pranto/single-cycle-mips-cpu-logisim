addi $sp, $zero, 15
sw $t0, 5($zero)
lw $t4, 5($zero)
beq $t4, $t0, label1
addi $t0, $zero, 0
j end
label1:
addi $t1, $zero, 1
end:
add $zero, $zero, $zero