# Route53 as DDNS
The python script serves the purpose to update the record on AWS Route53 so that my home server can be accessed remotely via Route53 as DDNS.
It works best with a service which runs upon a network connection has been established.


## Requirement
+ Python 3.X +
+ AWS CLI 2.X +

## Usage Example (eg.Ubuntu)
1. Prepare a trigger for the script. eg. sample.service
2. Put the service file under `/lib/systemd/system/`.
3. Reload to read the newly added service.   
   ```
   $ sudo systemctl daemon-reload
   ```
4. Enable service to start on reboot.  
   ```
   $ sudo systemctl enable sample.service  
   $ sudo systemctl start sample.service
   ```


## License
[MIT](LICENSE)


