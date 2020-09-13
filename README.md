# zju ecard turnover check
## 浙大校园卡消费流水查询

fill your studentID, studentPassword, ecardID in main function and run this script to check your ecard turnover. And you could define the start-date and end-date too. This script can only get 15 logs at once. Ofcourse you could modify it.

把浙大统一通行证的账号和密码、校园卡账号填入主函数里面，就可以进行当天的流水查询了。当然你也可以自定义查询起止日期，但是这个代码一次只能获得前15条记录（也可以自己改一改）

```python
def main():
    # default : quiry turnover of today
    sdate = time.strftime("%Y-%m-%d", time.localtime())
    edate = time.strftime("%Y-%m-%d", time.localtime())

    password = '密码写这里'      # like 'zju123456'
    userid = '学号写这里'        # like '3150101111'
    account = '校园卡卡号写这里' # like '121212'
    # if you wanna define the start date and end date
    # 如果要自定义查询日期，修改下面两行并取消其注释就可以了
    # sdate = '起始日期写这里' # like '2020-09-10'
    # edate = '结束日期写这里' # like '2020-09-10'
```
