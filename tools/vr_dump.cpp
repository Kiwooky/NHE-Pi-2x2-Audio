// Dumps a VeroRoute .vrt (parts, pins, painted cells) as JSON. Build like tools/vr_place.cpp.
// Usage: vr_dump docs/nhe-2x2-audio.vrt > docs/vr_layout.json
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

int main(int argc, char** argv)   // dump <in.vrt> -> JSON on stdout
{
	QApplication app(argc, argv);
	Board board; DataStream in(DataStream::READ);
	if ( !in.Open(argv[1]) ) { std::cerr << "cannot open\n"; return 1; }
	board.Load(in); in.Close();
	QJsonObject J;
	J["rows"] = board.GetRows(); J["cols"] = board.GetCols(); J["lyrs"] = board.GetLyrs();
	J["diags"] = (int) board.GetDiagsMode(); J["vero"] = board.GetVeroTracks();
	QJsonArray comps;
	for (const auto& o : board.m_compMgr.GetMapIdToComp())
	{
		const Component& c = o.second;
		if ( c.GetType() == COMP::TRACKS ) continue;
		QJsonObject C;
		C["name"] = QString::fromStdString(c.GetNameStr());
		C["value"] = QString::fromStdString(c.GetValueStr());
		C["type"] = QString::fromStdString(CompTypes::GetDefaultImportStr(c.GetType()));
		C["typeid"] = (int) c.GetType();
		C["placed"] = c.GetIsPlaced();
		C["dir"] = QString(QChar(c.GetDirection()));
		C["row"] = c.GetRow(); C["col"] = c.GetCol();
		C["rows"] = c.GetCompRows(); C["cols"] = c.GetCompCols();
		QJsonArray pins;
		for (size_t i = 0; i < c.GetNumPins(); i++)
		{
			int r = -1, k = -1; board.GetPinRowCol(o.first, i, r, k);
			QJsonArray p; p.append(r); p.append(k); p.append(c.GetNodeId(i)); pins.append(p);
		}
		C["pins"] = pins;
		comps.append(C);
	}
	J["comps"] = comps;
	QJsonArray cells;
	for (int l = 0; l < board.GetLyrs(); l++)
	for (int r = 0; r < board.GetRows(); r++) for (int k = 0; k < board.GetCols(); k++)
	{
		const Element* e = board.Get(l, r, k);
		const int nid = e->GetNodeId();
		if ( nid != BAD_NODEID || e->GetHasWire() ) { QJsonArray a; a.append(l); a.append(r); a.append(k); a.append(nid); a.append(e->GetHasWire()); cells.append(a); }
	}
	J["cells"] = cells;
	std::cout << QJsonDocument(J).toJson(QJsonDocument::Compact).toStdString() << "\n";
	return 0;
}
