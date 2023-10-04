# Setup the environment.

1. Spark, Scala and Kafka versions must be compatible. 
    - Download spark-3.1.2-bin-hadoop3.2 (this is the last build of Spark with Scala 2.12 as core dependency of pyspark is Scala 2.12)
        - https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz 
            - Extract with:
            ```
                gunzip -c spark-3.1.2-bin-hadoop3.2.tgz | tar xvf -
            ```
        - In active python environment run: 
            ```
                pip install pyspark==3.1.2
            ```
        - Once installed, check that your pyspark has the correct version of Scala using:
            ```
                spark-submit --version
            ```
    
    - Download kafka_2.12-3.1.2 (This version of Kafka natively supports Scala 2.12)
        - https://downloads.apache.org/kafka/3.1.2/kafka_2.12-3.1.2.tgz 
            - Extract with: 
                ```
                gunzip -c kafka_2.12-3.1.2.tgz | tar xvf -
                ```

2. Install Java Open Development Kit 11 (latest Java version compatible with Spark)
    - https://sparkbyexamples.com/pyspark/pyspark-exception-java-gateway-process-exited-before-sending-the-driver-its-port-number/

3. Create Java and Spark home environment variables (done in app.py)
    ```
        os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
        os.environ["SPARK_HOME"] = "/home/username/sources/spark-3.1.2-bin-hadoop3.2/"
    ```
    -  To check if Java and Spark home are properly configured, run in terminal:
            ```
            echo $JAVA_HOME
            ```
    &   
            ```
            echo $SPARK_HOME
            ```
4. Jar packages used in app.py must match the exact versions of the underlying infra (Spark, Scala, Kafka). App.py will download them automatically.
    ``` 
    https://mvnrepository.com/artifact/org.mongodb.spark/mongo-spark-connector_2.12/3.0.2)
    https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10_2.12/3.1.2)
    ```
5. Misc:

    - On Linux you may need to grant permissions to your Spark folder. 
        ```
        chmod +x /home/username/sources/spark-3.1.2-bin-hadoop3.2/bin/*
        ```
    - Sometimes Zookeper could hang and you may need to kill its process using.
        ```
        sudo service zookeeper stop 
        ```
If the above fail try: 
        ```
        su - zookeeper -c "export ZOOCFGDIR=/etc/zookeeper/conf ; export ZOOCFG=zoo.cfg ;source /etc/zookeeper/conf/zookeeper-env.sh ; /usr/lib/zookeeper/bin/zkServer.sh stop"
        ```

6. Provision remote MongoDB to store the kafka stream. Configuration is set in app.py to connect to a free tier, shared MongoDB cluster hosted on AWS through the public `cloud.mongodb.com` service. The cluster has dedicated database called `TwitterDB` and an underlying collection called `Tweets`. Remote access to the cluster is achieved through connection string using pymongodb driver and username with password. For ease of use, network configuration within mongodb cloud is set to allow all access (`0.0.0.0/0`).

# Windows Setup

    cd to kafka_2.12-3.1.2

1. Start zookeper & kafka servers
```
    bin/windows/zookeeper-server-start.bat config/zookeeper.properties
    bin/windows/kafka-server-start.bat config/server.properties
```
2. Create new Kafka topic
```
    bin/windows/kafka-topics.bat --create --topic twitter --bootstrap-server localhost:9092
```
3. Test the topic
```
    bin/windows/kafka-topics.bat --describe --topic twitter --bootstrap-server localhost:9092
```
4. Start the scripts 

Specific for the Windows setup is that if you start the scripts from VSCode you need to provide the full python.exe path of your active environment and then to add the full path to your python scripts.
```
    & D:/Dev/Python/Anaconda/envs/python3.10/python.exe d:/Dev/Projects/Kafka/producer.py
    & D:/Dev/Python/Anaconda/envs/python3.10/python.exe d:/Dev/Projects/Kafka/consumer.py
    & D:/Dev/Python/Anaconda/envs/python3.10/python.exe d:/Dev/Projects/Kafka/app.py
```
# Linux / MAC Setup

    cd to kafka_2.12-3.1.2

1. Start zookeper & kafka servers
```
    bin/zookeeper-server-start.sh config/zookeeper.properties
    bin/kafka-server-start.sh config/server.properties
```
2. Create new Kafka topic
```
    bin/kafka-topics.sh --create --topic twitter --bootstrap-server localhost:9092
```
3. Test the topic
```
    bin/kafka-topics.sh --describe --topic twitter --bootstrap-server localhost:9092
```
4. Start the scripts 

    cd to root and start in consecutive order:

```
    python3 producer.py
    python3 consumer.py
    python3 app.py
```