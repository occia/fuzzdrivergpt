ls /out/* | while read f;
do
  [ -x $f ] && {
    count=`strings $f | grep LLVMFuzzerTestOneInput | wc -l`;
    [ $count -gt 0 ] && echo $f;
  };
done

