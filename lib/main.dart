import 'dart:convert';
import 'dart:io';
import 'package:bubble/bubble.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:testing_app/secondary.dart';
void main() => runApp(MyApp());
class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chatbot Flask',
      theme: ThemeData(
        primaryColor: Colors.lightBlue[900],
        accentColor: Colors.cyan[600],
      ),
      home: MyHomePage(title: 'What U Can Bring'),
    );
  }
}
class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);
  final String title;
  @override
  _MyHomePageState createState() => _MyHomePageState();
}
class _MyHomePageState extends State<MyHomePage> {
  final GlobalKey<AnimatedListState> _listKey = GlobalKey();
  ScrollController _scrollController = new ScrollController();
  List<String> _data = [];
  static const String BOT_URL = "http://127.0.0.1:5000/bot"; // replace with server address
  TextEditingController _queryController = TextEditingController();
  final ScrollController _controller = ScrollController();
  @override
  Widget build(BuildContext context) {
    return Scaffold(
        backgroundColor: Colors.lightBlue[500],
      appBar: AppBar(
        leading: IconButton(
            icon: Icon(Icons.camera_alt, color: Colors.greenAccent, size: 35,),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => SecondRoute()),
              );
            },
          ),
        centerTitle: true,
        title: Text("What U Can Bring"),

      ),
      body: Container(
        child:Stack(
        children: <Widget>[
          AnimatedList(
            // key to call remove and insert from anywhere
              controller: _controller,
              key: _listKey,
              initialItemCount: _data.length,
              itemBuilder: (BuildContext context, int index, Animation animation){
                return _buildItem(_data[index], animation, index);
              }
          ),

          Align(
            alignment: Alignment.bottomCenter,

            child: TextField(
              decoration: InputDecoration(
                icon: Icon(Icons.message, color: Colors.green[200],),
                contentPadding: EdgeInsets.all(10.0),
                hintText: "Write Your Item",

              ),
              controller: _queryController,
              textInputAction: TextInputAction.send,
              onSubmitted: (msg){
                this._getResponse();
              },
            ),
          ),
        ],
      )
      ,
      )
    );
  }

  http.Client _getClient(){
    return http.Client();
  }
  void _getResponse(){
    if (_queryController.text.length>0){
      this._insertSingleItem(_queryController.text);
      var client = _getClient();
      try{
        client.post(BOT_URL, body: {"query" : _queryController.text},)
          ..then((response){
            Map<String, dynamic> data = jsonDecode(response.body);
            _insertSingleItem(data['response']+"<bot>");
            _controller.animateTo(

              _controller.position.maxScrollExtent,

              curve: Curves.easeOut,

              duration: const Duration(milliseconds: 300),

            );
          });
      }catch(e){
        print("Failed -> $e");
      }finally{
        client.close();
        _queryController.clear();
      }
    }
  }
  void _insertSingleItem(String message){
    _controller.animateTo(

      _controller.position.maxScrollExtent,

      curve: Curves.easeOut,

      duration: const Duration(milliseconds: 300),

    );
    _data.add(message);
    _listKey.currentState.insertItem(_data.length-1);
  }
  Widget _buildItem(String item, Animation animation,int index){
    bool mine = item.endsWith("<bot>");
    return SizeTransition(
        sizeFactor: animation,
        child: Padding(padding: EdgeInsets.only(top: 15),
          child: Container(

              alignment: mine ?  Alignment.topLeft : Alignment.topRight,
              child : Bubble(
                child: Text(
                    item.replaceAll("<bot>", ""),
                    style: TextStyle(
                      color: mine ? Colors.black : Colors.black),
                    ),
                  color: mine ? Colors.white : Colors.yellow,
                  padding: BubbleEdges.all(10),
                ),

              ),
        )
    );
  }
}



