urls=( edS6be3sk8oQ58N infBBW2Rc9TJwf7 76Esj3yDP9EiaGc AZmt47d48prCZZF
       9fZ4A7ENGR6sQrc B8HC3H4oqwcsWB3 t3zLJWWeirR5zmG YmkYgxM7xxrNAwj
       rMma6W9MBtQH9LX MzcZBCaxaojTZJx dfP6NXHmekQQrHR 2GnLRgPi8W2Dt5p
       MqtoESg2d9DsF2P ysGoJK6B3pLYaDB Ae32XwCpt7bHo9D AysWSPnxFS6e5B2
       4NcnJkPYWpkXrmb mBRfrnfEEEaKJ9m J63KxeCppK8ssGc NeqnHBNPWx4PRwd
       JdzZQCKiHaRfL9L DXnWtA5fymHBsxA HzgtF42Pf9AnxGm yy8FASeC8Dm54Sy
       TC8QekmjokmBkWA )
num_data=10
DATA_DIR=data
for i in $(seq 0 $num_data); do
    filename=$DATA_DIR/mantle"$(printf "%02d\n" $((i+1)))".tgz
    wget https://nextcloud.computecanada.ca/index.php/s/"${urls[$i]}"/download -O $filename
    tar -zxvf $filename -C $DATA_DIR
    rm $filename
done
