import asyncio
import logging
import time

# from websockets import connect
import websockets
from threading import Thread
import json

import websockets.legacy
import websockets.legacy.client
__author__ = {"Prajwal Kumar Jha": "pkumarjha@zscaler.com"}
class SocketConnector:
    def __init__(self, host, port, username, password, loggers=None):
        """
        This class is used to create an instance of SockerConnector, which can be used to connect to a remote machine
        and then execute commands on remote machine.

        :param str host: the remote machine's host. (this is localhost ip for now)
        :param str port: the port number on which websocket is running on server machine.
        """
        self.host = host
        self.URL = f"ws://{username}:{password}@{self.host}:{port}"
        self.conn = None
        self.loop = asyncio.get_event_loop()
        self.__keep_alive_thread = None
        # self.alive = False
        self.busy = False
        self.loggers= loggers if loggers else logging.Logger(name="agent", level="INFO")
        self.run(command="net session")

    def __keep_alive(self):
        try:
            while True:
                time.sleep(19)
                exit_code= self.run(command="keep-alive", keep_alive=False)
                if not exit_code.get('status'):
                    break
        except Exception as E:
            self.loggers.debug(f"{E}")
        finally:
            return {"status": False, "message":f"{E}"}


    def connect(self, keep_alive=True):
        conn = None
        retry = 6
        while conn is None and retry > 0:
            try:
                self.loggers.debug(f"Establishing connection with {self.URL}")
                conn= websockets.connect(self.URL,)
                
                if keep_alive and not self.__keep_alive_thread:
                    self.__keep_alive_thread = Thread(target= self.__keep_alive,daemon=True)
                    # self.alive=True
                    self.__keep_alive_thread.start()
                    # self.__keep_alive_thread.
                    # self.__keep_alive_thread.
            except Exception as e:
                self.loggers.warning(f"Failed to establish local websocket connection.. Retrying again after 5 second. {e}")
                time.sleep(5)
                conn = None
                retry -= 1

        if conn is None:
            self.loggers.error(f"Failed to establish connection with {self.URL}")
        
        return conn

    def run(self, command, cwd=None, keep_alive=True):
        try:
            while self.busy:
                time.sleep(1)
            # print(f"{self.busy} {command}")
            self.busy=True
            if cwd:
                command = ";".join([command, str(cwd)])
            data =json.loads(self.loop.run_until_complete(self.__execute_command(command, keep_alive)))
            self.busy=False
            return data
        except Exception as ex:
            self.loggers.warning(f"Failed to execute {command =}. {ex} self.busy = {self.busy}")
            return {"status": False, "message": f"{ex} self.busy = {self.busy}"}
    def pull_proc_info(self, procid:str, wait_for_output=False):
        data = self.run(command=f"pull_proc_info={procid}",keep_alive=False)
        if wait_for_output:
            while not data.get('status') and data.get('exit_code') is None:
                time.sleep(5)
                data = self.run(command=f"pull_proc_info={procid}",keep_alive=False)
        return data

    async def __execute_command(self, command, keep_alive=True):
        if self.conn is None:
            self.loggers.debug(f"Connection object is None. creating connection with {self.URL}")
            self.conn = await self.connect(keep_alive=keep_alive)
        await self.conn.send(command)
        return await self.conn.recv()
    
    async def __disconnect(self):
        if self.conn is not None:
            await self.conn.send("close")
            data = json.loads(await self.conn.recv())
            if data.get('status'):
                await self.conn.close(reason="Terminating the connection")
                return {"status": True, "message": "Successfully terminated the connection"}
            else: 
                return {"status":False, "message": "Unable to disconnect"}
                # await self.conn.close_connection()
            

    def disconnect(self):
        try:
            while self.busy:
                time.sleep(2)
            self.busy=True
            data = self.loop.run_until_complete(self.__disconnect())
            self.busy=False
            return data
        except Exception as ex:
            self.loggers.warning(f"Failed to disconnect. {ex}")
            return {"status": False, "message": f"{ex}"}
    
    def broadcast_task(self , task:dict):
        send_task = self.run(command=f"add_task={json.dumps(task)}", keep_alive=False)
        if not send_task.get('status'):
            return send_task
        ret_data = self.pull_proc_info(procid=send_task['id'], wait_for_output=True)
        return ret_data
    def __get_first_pending_task(self, id=None):
        get_pending_task = self.run(command="fetch_pending_id" if not id else f"fetch_pending_id={id}", keep_alive=False)
        # if not get_pending_task.get('status'):
        #     return get_pending_task
        return get_pending_task
    
    def exec_pending_task(self):
        try:
            exit_code = self.__get_first_pending_task()
            if exit_code.get('status'):
                exit_code = self.__get_first_pending_task(id=exit_code.get('id'))
            return exit_code
        except Exception as E:
            self.loggers.debug(f"{E}")
        finally:
            return {"status": False, "message":f"{E}"}
    # def __del__(self):
    #     print("\n\nSomething\n\n")
    #     if self.__keep_alive_thread is not None:
    #         self.alive =False