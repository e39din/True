# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0

123
456
789
= array2d

1 = i
1 = j

array2d:y:i:x:j % 2 == 0 ? X => array2d:y:i:x:j
array2d:y:i:x:j % 2 == 1 ? O => array2d:y:i:x:j

j + 1 ?=> j
j > 3 ? 1 => j
j == 1 ? i + 1 ?=> i
i > 3 ? ::agent:finish
