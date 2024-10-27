import random
import sys
#执行时间通过计数的方式实现

#首先定义PCB块
class PCB:
    def __init__(self, pid):    
        self.pid = pid                               #PCB的pid由主程序的调用实现
        self.priority = 0                            #新定义的进程都应该进入优先级最高的队列
        self.state = 'created'                       #定义进程的初始状态
        self.needing_time = random.randint(1, 75)    #随机生成进程执行完所需时间
        self.executing_time = 0                      #定义进程已经执行的时间
        self.waiting_time = 0                        #在遇到I/O时间阻塞时等待的时间
        self.next = None                             #PCB块的控制通过链表实现

#定义PCB块的链表
class PCBList:
    def __init__(self):
        self.head = None        #定义链表的头指针

    #定义方法将进程添加到队列的队尾
    def add_process(self, process):
        if not self.head:               #如果链表为空，则进入队列的进程应该作为表头
            self.head = process
        else:
            current = self.head         #current用来实现链表的迭代
            while current.next:         #循环迭代链表，直到最后的指针为空
                current = current.next  #找到最后一个指针
            current.next = process      #最后一个指针指向新添加的进程

    #定义方法用来取出链表中的进程
    def remove_process(self, process):
        if process == self.head:        #确定取出的进程是否为表头
            self.head = self.head.next  #取出表头
            process.next = None
        else:
            current = self.head
            while current.next and current.next != process:
                current = current.next
            if current.next:
                to_remove = current.next
                current.next = current.next.next
                to_remove.next = None   #将要移除的进程断开与链表的连接
                
    #定义方法用来打印队列中所有进程的PID 
    def print_process(self):
        current = self.head
        pids = []
        while current:
            pids.append(current.pid)
            current = current.next
        return pids
                
#定义调度器
class Scheduler:
    #首先初始化调度器
    def __init__(self):
        self.ready_queue = [PCBList() for _ in range(4)]   #初始化四条优先级就绪队列
        self.block_queue = PCBList()                       #初始化一条阻塞队列
        self.running_process = None                        #初始化一个执行进程
        self.time_slice = [5, 10, 20 ,40]                  #初始化就绪队列对应的时间片
        self.current_time = 0                              #记录调度器运行的时间

    #定义方法用来创建进程
    def create_process(self, pid):
        new_process = PCB(pid)                             #通过pid来创建一个PCB块
        self.ready_queue[0].add_process(new_process)       #将新创建的进程放入优先级最高的就绪队列
        new_process.state = 'ready'                        #转换PCB块的状态为就绪，默认除CPU外其他资源已经分配好
        print(f"\nPID：{pid}\n优先级：{new_process.priority}\n状态：{new_process.state}\n所需执行时间：{new_process.needing_time}\n已执行时间：{new_process.executing_time}\nI/O等待时间：{new_process.waiting_time}\n当前时间：{self.current_time}")   #打印进程的初始状态

    #定义方法用来撤销进程(指非正常撤销)
    def revoke_process(self):
        if not self.running_process:
            return
        
        if random.random() < 0.005:                        #随机触发非正常撤销
            print(f"\n\n----进程{self.running_process.pid}因遭遇异常情况被撤销----")
            self.running_process.state = 'terminated'
            print(f"PID：{self.running_process.pid}\n优先级：{self.running_process.priority}\n状态：{self.running_process.state}\n所需执行时间：{self.running_process.needing_time}\n已执行时间：{self.running_process.executing_time}\nI/O等待时间：{self.running_process.waiting_time}\n当前时间：{self.current_time}")
            
            #从就绪队列中移除进程
            for queue in self.ready_queue:
                if queue.head and queue.head.pid == self.running_process.pid:
                    queue.remove_process(self.running_process)
                    break
        
            #清理当前运行的进程
            self.running_process = None
            
            #打印当前队列的情况
            print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
            print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")

    #定义方法用来阻塞进程
    def block_process(self, process):
        process.waiting_time = random.randint(1, 30)       #随机生成I/O阻塞时间
        self.block_queue.add_process(process)              #将阻塞进程添加到阻塞队列
        process.state = 'blocked'                          #设置状态
        print(f"\n\n----进程{process.pid}被阻塞，等待时间为{process.waiting_time}----")
        print(f"PID：{process.pid}\n优先级：{process.priority}\n状态：{process.state}\n所需执行时间：{process.needing_time}\n已执行时间：{process.executing_time}\nI/O等待时间：{process.waiting_time}\n当前时间：{self.current_time}")
        self.ready_queue[process.priority].remove_process(process)
        print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
        print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
        
    #定义方法用来唤醒进程
    def wakeup_process(self):
        if not self.block_queue.head:                      #阻塞队列为空直接返回
            return
        current = self.block_queue.head                    #从队首开始迭代检查
        while current:                                     #迭代检查整条队列的等待情况
            current.waiting_time -= 1
            if current.waiting_time <= 0:                  #如果等待时间结束了就唤醒进程
                print(f"\n\n----唤醒进程[{current.pid}]，当前时间为{self.current_time}----")
                self.ready_queue[current.priority].add_process(current)
                current.state = 'ready'
                print(f"PID：{current.pid}\n优先级：{current.priority}\n状态：{current.state}\n所需执行时间：{current.needing_time}\n已执行时间：{current.executing_time}\nI/O等待时间：{current.waiting_time}\n当前时间：{self.current_time}")
                next_process = current.next                #保存下一个进程的引用
                self.block_queue.remove_process(current)   #将唤醒的进程从阻塞队列中删除
                print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
                print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
                current = next_process                     #更新current为下一个进程
            else:
                current = current.next                     #迭代阻塞队列
                
    #定义RR轮转调度算法
    def RR_process(self, queue):
        if not queue.head:                                 #先检查最后一条就绪队列是否为空
            return 
                     
        time_slice = self.time_slice[3]                    #获取当前队列的时间片

        while queue.head:

            self.running_process = queue.head              #首先执行队列的第一个进程
            self.running_process.state = 'running'         #改变当前进程的状态

            time_slice = self.time_slice[3]                #重置时间片
            print(f"\n\n----进程{self.running_process.pid}开始执行，时间片为{time_slice}----")
            print(f"PID：{self.running_process.pid}\n优先级：{self.running_process.priority}\n状态：{self.running_process.state}\n所需执行时间：{self.running_process.needing_time}\n已执行时间：{self.running_process.executing_time}\nI/O等待时间：{self.running_process.waiting_time}\n当前时间：{self.current_time}")
            print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
            print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
            
            #如果还有时间片并且程序没有执行完则进入执行过程
            while time_slice > 0 and self.running_process.executing_time < self.running_process.needing_time:
                
                self.running_process.executing_time += 1    #执行时间增加
                self.current_time += 1                      #调度器运行时间增加
                time_slice -= 1                             #时间片时间减少
                
                #检查进程是否会执行小于时间片的时间完成
                if self.running_process.executing_time >= self.running_process.needing_time:
                    self.running_process.state = 'terminated'   #设置进程状态为已完成
                    queue.remove_process(self.running_process)  #将已完成的进程移除就绪队列
                    print(f"\n\n----进程{self.running_process.pid}执行完毕----")
                    print(f"PID：{self.running_process.pid}\n优先级：{self.running_process.priority}\n状态：{self.running_process.state}\n所需执行时间：{self.running_process.needing_time}\n已执行时间：{self.running_process.executing_time}\nI/O等待时间：{self.running_process.waiting_time}\n当前时间：{self.current_time}")
                    print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
                    print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
                    self.running_process = None                 #当前没有正在执行的程序
                    self.wakeup_process()
                    for j in range(len(self.ready_queue) - 1):
                        if self.ready_queue[j].head:
                            self.MFQ_process()
                            return
                    break                                       #退出当前进程的执行

                self.wakeup_process()
                
                #实现抢占调度
                for j in range(len(self.ready_queue) - 1):
                    if self.ready_queue[j].head:
                        self.ready_queue[len(self.ready_queue) - 1].add_process(self.running_process)
                        self.ready_queue[len(self.ready_queue) - 1].remove_process(self.running_process)
                        self.running_process.state = 'ready'
                        print(f"\n----进程{self.running_process.pid}被更高优先级的进程{self.ready_queue[j].head.pid}抢占----")
                        print(f"PID：{self.running_process.pid}\n优先级：{self.running_process.priority}\n状态：{self.running_process.state}\n所需执行时间：{self.running_process.needing_time}\n已执行时间：{self.running_process.executing_time}\nI/O等待时间：{self.running_process.waiting_time}\n当前时间：{self.current_time}")
                        print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
                        print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
                        self.running_process = None
                        self.MFQ_process()
                        return

                self.revoke_process()
                
                if self.running_process:
                    if time_slice > 0:
                        #模拟I/O操作
                        if random.random() < 0.01:  #1%的概率触发I/O操作
                            self.block_process(self.running_process)
                            self.running_process = None
                            break  
                else:
                    break

            if self.running_process and self.running_process.executing_time < self.running_process.needing_time:
                queue.remove_process(self.running_process)      #将上一个时间片没有执行完的程序移除
                queue.add_process(self.running_process)         #将从队首移除的程序放在队尾
                self.running_process.state = 'ready'            #将其状态更新为就绪
                print(f"\n\n----进程{self.running_process.pid}在当前时间片没有执行完，进入就绪队列{self.running_process.priority}----")
                print(f"PID：{self.running_process.pid}\n优先级：{self.running_process.priority}\n状态：{self.running_process.state}\n所需执行时间：{self.running_process.needing_time}\n已执行时间：{self.running_process.executing_time}\nI/O等待时间：{self.running_process.waiting_time}\n当前时间：{self.current_time}")
                print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
                print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
                self.running_process = None                     #将正在执行的进程设置为空

    #定义MFQ算法
    def MFQ_process(self):
        for i in range(len(self.ready_queue)):
            while self.ready_queue[i].head:
                
                if i == len(self.ready_queue) - 1:
                    self.RR_process(self.ready_queue[i])
                    continue
                
                self.running_process = self.ready_queue[i].head
                self.running_process.state = 'running'

                time_slice = self.time_slice[i]                 #重置时间片
                print(f"\n\n----进程{self.running_process.pid}开始执行，时间片为{self.time_slice[i]}----")
                print(f"PID：{self.running_process.pid}\n优先级：{self.running_process.priority}\n状态：{self.running_process.state}\n所需执行时间：{self.running_process.needing_time}\n已执行时间：{self.running_process.executing_time}\nI/O等待时间：{self.running_process.waiting_time}\n当前时间：{self.current_time}")
                print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
                print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
                
                while time_slice > 0 and self.running_process.executing_time < self.running_process.needing_time:
                    
                    self.running_process.executing_time += 1    #执行时间增加
                    self.current_time += 1                      #调度器运行时间增加
                    time_slice -= 1                             #时间片时间减少
                    
                    if self.running_process.executing_time >= self.running_process.needing_time:
                        self.running_process.state = 'terminated'
                        print(f"\n\n----进程{self.running_process.pid}执行完毕----")
                        print(f"PID：{self.running_process.pid}\n优先级：{self.running_process.priority}\n状态：{self.running_process.state}\n所需执行时间：{self.running_process.needing_time}\n已执行时间：{self.running_process.executing_time}\nI/O等待时间：{self.running_process.waiting_time}\n当前时间：{self.current_time}")
                        self.ready_queue[i].remove_process(self.running_process)
                        print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
                        print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
                        self.running_process = None             #当前没有正在执行的程序
                        self.wakeup_process()
                        for j in range(i):
                            if self.ready_queue[j].head:
                                self.MFQ_process()
                                return
                        break
                    
                    self.wakeup_process()
                    
                    #实现抢占调度
                    for j in range(i):
                        if self.ready_queue[j].head:
                            self.ready_queue[i].add_process(self.running_process)
                            self.ready_queue[i].remove_process(self.running_process)
                            self.running_process.state = 'ready'
                            print(f"\n----进程{self.running_process.pid}被更高优先级的进程{self.ready_queue[j].head.pid}抢占，进入就绪队列{self.running_process.priority}----")
                            print(f"PID：{self.running_process.pid}\n优先级：{self.running_process.priority}\n状态：{self.running_process.state}\n所需执行时间：{self.running_process.needing_time}\n已执行时间：{self.running_process.executing_time}\nI/O等待时间：{self.running_process.waiting_time}\n当前时间：{self.current_time}")
                            print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
                            print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
                            self.running_process = None
                            self.MFQ_process()
                            return

                    self.revoke_process()

                    if self.running_process:
                        if time_slice > 0:
                            #模拟I/O操作
                            if random.random() < 0.01:                   #1%的概率触发I/O操作
                                self.block_process(self.running_process)
                                self.running_process = None
                                break
                    else:
                        break

                if self.running_process and self.running_process.executing_time < self.running_process.needing_time:
                    if i + 1 < len(self.ready_queue):
                        self.ready_queue[i + 1].add_process(self.running_process)
                        self.running_process.priority = i + 1
                        print(f"\n\n----进程{self.running_process.pid}在当前时间片没有执行完，进入就绪队列{self.running_process.priority}----")
                    else:
                        self.ready_queue[i].add_process(self.running_process)
                        print(f"\n\n----进程{self.running_process.pid}在当前时间片没有执行完，进入就绪队列{self.running_process.priority}----")

                    self.running_process.state = 'ready'
                    print(f"PID：{self.running_process.pid}\n优先级：{self.running_process.priority}\n状态：{self.running_process.state}\n所需执行时间：{self.running_process.needing_time}\n已执行时间：{self.running_process.executing_time}\nI/O等待时间：{self.running_process.waiting_time}\n当前时间：{self.current_time}")
                    self.ready_queue[i].remove_process(self.running_process)
                    print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
                    print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
                    self.running_process = None
    #定义方法用来调度进程
    def schedule_process(self):
        while True:
            self.MFQ_process()
            # 当所有就绪队列为空时，检查阻塞队列
            if not any([q.head for q in self.ready_queue]) and self.block_queue.head:
                wakeup_list = []
                current = self.block_queue.head
                self.current_time += 1
                while current:
                    current.waiting_time -= 1
                    if current.waiting_time <= 0:
                        print(f"\n\n----唤醒进程：[{current.pid}]，当前时间为：{self.current_time}----")
                        wakeup_list.append(current)
                        current.state = 'ready'
                        print(f"PID：{current.pid}\n优先级：{current.priority}\n状态：{current.state}\n所需执行时间：{current.needing_time}\n已执行时间：{current.executing_time}\nI/O等待时间：{current.waiting_time}\n当前时间：{self.current_time}")
                        print(f"当前就绪队列的情况为：队列0：{self.ready_queue[0].print_process()}\n                      队列1：{self.ready_queue[1].print_process()}\n                      队列2：{self.ready_queue[2].print_process()}\n                      队列3：{self.ready_queue[3].print_process()}")
                        print(f"当前阻塞队列的情况为：       {self.block_queue.print_process()}\n")
                    current = current.next

                # 将唤醒的进程添加到就绪队列
                for process in wakeup_list:
                    self.ready_queue[process.priority].add_process(process)
                    self.block_queue.remove_process(process)   #将唤醒的进程从阻塞队列中删除
                    
                # 再次检查就绪队列，以执行唤醒的进程
                if any([q.head for q in self.ready_queue]):
                    continue
            if not any([q.head for q in self.ready_queue]) and not self.block_queue.head:
                break  # 所有队列都为空，结束调度

def main():
    scheduler = Scheduler()

    count = int(input("请输入要创建的进程数目："))

    #创建一些进程
    print(f"\n----即将创建{count}个进程----")

    for i in range(count):
        scheduler.create_process(i)

    print(f"\n----进程创建完毕----\n\n")
    
    print(f"当前就绪队列的情况为：队列0：{scheduler.ready_queue[0].print_process()}\n                      队列1：{scheduler.ready_queue[1].print_process()}\n                      队列2：{scheduler.ready_queue[2].print_process()}\n                      队列3：{scheduler.ready_queue[3].print_process()}")
    print(f"当前阻塞队列的情况为：       {scheduler.block_queue.print_process()}\n")
    
    #开始调度
    print(f"\n----开始调度进程----")

    scheduler.schedule_process()

    #打印最终结果
    print("\n----所有进程均已执行完毕----\n\n")
    sys.exit()

if __name__ == "__main__":
    main()