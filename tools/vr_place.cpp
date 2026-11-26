// Places a VeroRoute netlist at the positions in docs/vr_place.json and paints the tracks, writing a .vrt.
// Build against the VeroRoute 2.40 sources (Src/*.cpp minus main, dialogs, mainwindow, myscrollarea) and Qt 5.
// Usage: vr_place docs/nhe-2x2-audio.net docs/vr_place.json docs/nhe-2x2-audio.vrt
#include <sstream>
#include <iostream>
#include <fstream>
#include <map>
#include <set>
#include <list>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <memory>
#include <cmath>
#include <climits>
#include <cassert>
#include <array>
#include <functional>
#include <iomanip>
#include <QtWidgets>
#include <QtNetwork>
#define private public
#define protected public
#include "Board.h"
#include "TemplateManager.h"
#undef private
#undef protected
#include <QApplication>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <iostream>
int main(int argc, char** argv)   // place <netlist> <placement.json> <out.vrt>
{
	QApplication app(argc, argv);
	TemplateManager templateMgr; templateMgr.AddDefaults();
	Board board;
	std::string err; bool typeOK = true;
	if ( !board.Import(templateMgr, argv[1], err, true, typeOK) ) { std::cout << "import failed: " << err << "\n"; return 1; }
	QFile f(argv[2]); f.open(QIODevice::ReadOnly);
	const QJsonObject J = QJsonDocument::fromJson(f.readAll()).object();
	const int R = J["rows"].toInt(), C = J["cols"].toInt();
	const QJsonObject pos = J["pos"].toObject();

	std::vector<int> ids;
	for (const auto& o : board.m_compMgr.GetMapIdToComp()) if ( o.second.GetType() != COMP::TRACKS ) ids.push_back(o.first);
	for (int id : ids) { Component& c = board.m_compMgr.GetComponentById(id); if ( c.GetIsPlaced() ) board.TakeOff(c); }
	if ( board.GetRows() < R || board.GetCols() < C )
		board.GrowThenPan(0, std::max(0, R - board.GetRows()), std::max(0, C - board.GetCols()), 0, 0);
	int nPlaced = 0, nBad = 0;
	for (int id : ids)
	{
		Component& c = board.m_compMgr.GetComponentById(id);
		const QString name = QString::fromStdString(c.GetNameStr());
		if ( !pos.contains(name) ) { std::cout << "no position for " << c.GetNameStr() << "\n"; nBad++; continue; }
		const QJsonArray tgt = pos[name].toArray();
		bool done = false;
		for (char d : std::string("WENS"))
		{
			c.SetDirection(d);
			std::map<size_t, std::pair<int,int>> loc;
			for (int r = 0; r < c.GetCompRows(); r++) for (int k = 0; k < c.GetCompCols(); k++)
			{
				const CompElement* e = c.GetCompElement(r, k);
				if ( e && e->GetPinIndex() != BAD_PININDEX ) loc[e->GetPinIndex()] = {r, k};
			}
			if ( loc.size() != (size_t) tgt.size() ) { continue; }
			const int r0 = tgt[0].toArray()[0].toInt() - loc[0].first, c0 = tgt[0].toArray()[1].toInt() - loc[0].second;
			bool ok = true;
			for (size_t i = 0; i < loc.size(); i++)
				ok = ok && loc[i].first + r0 == tgt[(int)i].toArray()[0].toInt() && loc[i].second + c0 == tgt[(int)i].toArray()[1].toInt();
			if ( !ok ) continue;
			c.SetRow(r0); c.SetCol(c0);
			if ( board.PutDown(c) ) { done = true; nPlaced++; break; }
			std::cout << "PutDown failed for " << c.GetNameStr() << " dir " << d << "\n";
		}
		if ( !done ) { std::cout << "could not place " << c.GetNameStr() << " (pins " << tgt.size() << ")\n"; nBad++; }
	}
	// paint the tracks
	int nTrackBad = 0;
	for (const auto& tv : J["tracks"].toArray())
	{
		const QJsonArray t = tv.toArray(); const std::string net = t[0].toString().toStdString();
		const QJsonArray cells = t[1].toArray();
		int nodeId = BAD_NODEID;
		for (const auto& cv : cells) { const auto a = cv.toArray(); int nid = board.Get(0, a[0].toInt(), a[1].toInt())->GetNodeId(); if ( nid != BAD_NODEID ) { if ( nodeId == BAD_NODEID ) nodeId = nid; else if ( nid != nodeId ) { std::cout << "net " << net << ": two node ids\n"; nTrackBad++; } } }
		if ( nodeId == BAD_NODEID ) { std::cout << "net " << net << ": no pin on its track\n"; nTrackBad++; continue; }
		for (const auto& cv : cells) { const auto a = cv.toArray(); board.SetNodeIdByUser(0, a[0].toInt(), a[1].toInt(), nodeId, false); }
	}
	// check: every cell of each track now carries its net
	for (const auto& tv : J["tracks"].toArray())
	{
		const QJsonArray t = tv.toArray(); std::set<int> s;
		for (const auto& cv : t[1].toArray()) { const auto a = cv.toArray(); s.insert(board.Get(0, a[0].toInt(), a[1].toInt())->GetNodeId()); }
		if ( s.size() != 1 || *s.begin() == BAD_NODEID ) { std::cout << "track check failed: " << t[0].toString().toStdString() << "\n"; nTrackBad++; }
	}
	DataStream out(DataStream::WRITE);
	if ( !out.Open(argv[3]) ) { std::cout << "cannot write\n"; return 1; }
	board.Save(out); out.Close();
	// reload to make sure the file reads back
	Board b2; DataStream in(DataStream::READ);
	in.Open(argv[3]); b2.Load(in); in.Close();
	int n2 = 0; for (const auto& o : b2.m_compMgr.GetMapIdToComp()) if ( o.second.GetType() != COMP::TRACKS && o.second.GetIsPlaced() ) n2++;
	std::cout << "placed " << nPlaced << " of " << ids.size() << ", bad " << nBad << ", track problems " << nTrackBad
	          << ", grid " << board.GetRows() << "x" << board.GetCols() << ", reloaded placed " << n2 << "\n";
	return (nBad || nTrackBad) ? 1 : 0;
}
